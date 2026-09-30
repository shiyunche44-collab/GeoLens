import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_workspaces_are_isolated(client: TestClient) -> None:
    pid = client.post("/projects", json={"name": "Mine"}).json()["id"]
    other = {"X-Workspace-Id": str(uuid.uuid4())}

    assert client.get(f"/projects/{pid}").status_code == 200
    assert client.get(f"/projects/{pid}", headers=other).status_code == 404
    assert client.get("/projects", headers=other).json() == []
    r = client.post(f"/projects/{pid}/brands", json={"name": "X"}, headers=other)
    assert r.status_code == 404
