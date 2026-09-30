"""Every registered engine adapter must satisfy the EngineAdapter contract.

Parametrized over the registry: a new adapter is tested automatically, and
fails until it ships a recorded fixture in tests/fixtures/engines/<id>.json.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from geolens.modules.collection.adapters import registry
from geolens.modules.collection.adapters.base import EngineAdapter, QueryRequest
from geolens.modules.collection.adapters.openai_compatible import SPECS, OpenAICompatibleAdapter

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "engines"
SPEC_BY_ID = {s.engine_id: s for s in SPECS}


def _fixture(engine_id: str) -> dict[str, Any]:
    path = FIXTURES / f"{engine_id}.json"
    assert path.exists(), f"missing recorded fixture {path.name} for engine {engine_id!r}"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


@pytest.mark.parametrize("engine_id", registry.registered_ids())
def test_adapter_contract(engine_id: str, monkeypatch: pytest.MonkeyPatch) -> None:
    fx = _fixture(engine_id)
    adapter = registry.get(engine_id)

    assert isinstance(adapter, EngineAdapter)
    assert adapter.engine_id == engine_id
    assert adapter.region in ("cn", "global")
    assert adapter.mode in ("api", "browser", "serp", "mock")
    assert adapter.fidelity in ("ui", "api_search", "api_no_search", "synthetic")

    req = QueryRequest(prompt=fx["prompt"])
    with respx.mock(assert_all_called=False) as router:
        if isinstance(adapter, OpenAICompatibleAdapter):
            spec = SPEC_BY_ID[engine_id]
            monkeypatch.setenv(spec.key_env, "test-key")
            route = router.post(f"{spec.base_url}/chat/completions").mock(
                return_value=httpx.Response(200, json=fx["response"])
            )
        raw = asyncio.run(adapter.query(req))
        if isinstance(adapter, OpenAICompatibleAdapter):
            sent = json.loads(route.calls.last.request.content)
            assert sent["messages"][-1]["content"] == fx["prompt"]
            assert route.calls.last.request.headers["Authorization"] == "Bearer test-key"

    assert raw.engine_id == engine_id
    json.dumps(raw.payload)  # the raw snapshot must be JSON-serializable

    parsed = adapter.parse(raw)
    assert parsed.text.strip()
    assert len(parsed.citations) >= fx["expect"]["min_citations"]
    assert all(c.url.startswith(("http://", "https://")) for c in parsed.citations)


def test_api_engines_are_disabled_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for spec in SPECS:
        monkeypatch.delenv(spec.key_env, raising=False)
    assert set(registry.available_ids()) == {"mock-cn", "mock-global"}
