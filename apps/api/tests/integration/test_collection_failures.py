"""A run must always finish: every task ends done or failed, transient errors retry."""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from geolens.modules.collection import service as collection
from geolens.modules.collection.adapters import registry
from geolens.modules.collection.adapters.base import (
    ParsedAnswer,
    QueryRequest,
    RawResponse,
    TransientEngineError,
)

pytestmark = pytest.mark.integration


class ScriptedAdapter:
    """Fails according to `script` (one entry per call), then answers."""

    region = "cn"
    mode = "mock"
    fidelity = "synthetic"
    display_name = "scripted"

    def __init__(self, engine_id: str, script: list[Exception | None]) -> None:
        self.engine_id = engine_id
        self.script = script
        self.calls = 0

    async def query(self, req: QueryRequest) -> RawResponse:
        step = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        if step is not None:
            raise step
        return RawResponse(self.engine_id, {"answer": "GeoLens 是一个选择"}, units=1)

    def parse(self, raw: RawResponse) -> ParsedAnswer:
        return ParsedAnswer(text=raw.payload["answer"])


@pytest.fixture
def engine() -> Iterator[Any]:
    registered: list[str] = []

    def install(script: list[Exception | None]) -> ScriptedAdapter:
        adapter = ScriptedAdapter(f"scripted-{len(registered)}", script)
        registry.register(adapter.engine_id, lambda: adapter)
        registered.append(adapter.engine_id)
        return adapter

    yield install
    for eid in registered:
        registry.unregister(eid)


def _run(client: TestClient, engine_id: str) -> dict[str, Any]:
    pid = client.post("/projects", json={"name": "F"}).json()["id"]
    client.post(f"/projects/{pid}/brands", json={"name": "GeoLens"})
    client.post(f"/projects/{pid}/prompts", json={"text": "q"})
    run = client.post(
        f"/projects/{pid}/runs", json={"engines": [engine_id], "samples_per_prompt": 1}
    )
    assert run.status_code == 202, run.text
    result: dict[str, Any] = client.get(f"/runs/{run.json()['id']}").json()
    return result


def test_permanent_error_fails_task_and_finishes_run(client: TestClient, engine: Any) -> None:
    adapter = engine([ValueError("bad request")])
    run = _run(client, adapter.engine_id)
    assert (run["status"], run["failed_tasks"], run["done_tasks"]) == ("failed", 1, 0)


def test_transient_error_is_retried_then_succeeds(client: TestClient, engine: Any) -> None:
    adapter = engine([TransientEngineError("503"), None])
    run = _run(client, adapter.engine_id)
    assert (run["status"], run["done_tasks"]) == ("completed", 1)
    assert adapter.calls == 2


def test_transient_errors_give_up_after_max_attempts(client: TestClient, engine: Any) -> None:
    adapter = engine([TransientEngineError("429")])
    run = _run(client, adapter.engine_id)
    assert (run["status"], run["failed_tasks"]) == ("failed", 1)
    assert adapter.calls == collection.MAX_ATTEMPTS


def test_storage_failure_fails_task_instead_of_hanging(
    client: TestClient, engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    class BrokenStorage:
        def put_json(self, key: str, data: dict[str, Any]) -> str:
            raise OSError("bucket unavailable")

    monkeypatch.setattr(collection, "get_storage", lambda: BrokenStorage())
    adapter = engine([None])
    run = _run(client, adapter.engine_id)
    assert (run["status"], run["failed_tasks"]) == ("failed", 1)
