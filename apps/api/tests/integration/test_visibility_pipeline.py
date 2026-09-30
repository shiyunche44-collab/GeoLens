"""End-to-end thin slice: project → run (mock engines) → snapshots → analysis → metrics."""

import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def _seed_project(client: TestClient) -> str:
    project = client.post("/projects", json={"name": "Demo", "primary_domain": "geolens.io"})
    assert project.status_code == 201, project.text
    pid = project.json()["id"]
    brands = [
        {"name": "GeoLens", "domains": ["geolens.example.com"]},
        {"name": "RankPilot", "is_competitor": True, "domains": ["rankpilot.example.com"]},
        {"name": "Citely", "aliases": ["citely.ai"], "is_competitor": True},
    ]
    for b in brands:
        assert client.post(f"/projects/{pid}/brands", json=b).status_code == 201
    for q in ["最好的 GEO 分析工具有哪些？", "How do I track brand visibility in ChatGPT?"]:
        assert client.post(f"/projects/{pid}/prompts", json={"text": q}).status_code == 201
    return pid


def test_run_produces_snapshots_facts_and_metrics(client: TestClient) -> None:
    pid = _seed_project(client)
    engines = {e["id"] for e in client.get("/engines").json()}
    assert {"mock-cn", "mock-global"} <= engines

    run = client.post(
        f"/projects/{pid}/runs",
        json={"engines": ["mock-cn", "mock-global"], "samples_per_prompt": 3},
    )
    assert run.status_code == 202, run.text
    run_id = run.json()["id"]

    # Celery runs eagerly in tests, so the whole chain has finished by now.
    done = client.get(f"/runs/{run_id}").json()
    assert done["status"] == "completed"
    assert done["total_tasks"] == done["done_tasks"] == 2 * 2 * 3

    responses = client.get(f"/runs/{run_id}/responses").json()
    assert len(responses) == 12
    assert all(r["answer_text"] and r["fidelity"] == "synthetic" for r in responses)

    metrics = client.get(f"/projects/{pid}/metrics").json()
    overall = [m for m in metrics["summary"] if m["engine_id"] == "all"]
    assert {m["brand_name"] for m in overall} == {"GeoLens", "RankPilot", "Citely"}
    assert all(m["mention_rate"]["n"] == 12 for m in overall)
    sov_total = sum(m["share_of_voice"] or 0 for m in overall)
    assert sov_total == pytest.approx(1.0)
    per_engine = {m["engine_id"] for m in metrics["summary"]}
    assert per_engine == {"all", "mock-cn", "mock-global"}
    assert metrics["daily"], "daily series should not be empty"


def test_redelivery_and_reanalysis_are_idempotent(client: TestClient) -> None:
    from geolens.core.db import session_scope
    from geolens.core.tenancy import workspace_context
    from geolens.modules.analysis import service as analysis
    from geolens.modules.collection import service as collection
    from geolens.modules.collection.repository import QueryTaskRepository
    from geolens.modules.identity.public import ensure_default_workspace
    from geolens.modules.metrics import service as metrics

    pid = _seed_project(client)
    run_id = client.post(f"/projects/{pid}/runs", json={"engines": ["mock-cn"]}).json()["id"]
    before = client.get(f"/projects/{pid}/metrics").json()
    responses = client.get(f"/runs/{run_id}/responses").json()

    with workspace_context(ensure_default_workspace()):
        with session_scope() as s:
            task_ids = [t.id for t in QueryTaskRepository(s).list()]
        for tid in task_ids:  # a redelivered queue message must not collect twice
            collection.collect(tid)
        for r in responses:  # re-analysis replaces facts instead of duplicating them
            analysis.analyze_response(uuid.UUID(r["id"]))
        metrics.recompute_project(uuid.UUID(pid))

    assert len(client.get(f"/runs/{run_id}/responses").json()) == len(responses)
    assert client.get(f"/projects/{pid}/metrics").json() == before


def test_unknown_engine_is_rejected(client: TestClient) -> None:
    pid = _seed_project(client)
    r = client.post(f"/projects/{pid}/runs", json={"engines": ["no-such-engine"]})
    assert r.status_code == 422
