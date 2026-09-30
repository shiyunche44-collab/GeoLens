"""The committed openapi.json is the API contract the web app is generated from."""

import json
from pathlib import Path

from geolens.app.main import app

SNAPSHOT = Path(__file__).resolve().parents[2] / "openapi.json"


def test_openapi_snapshot_is_up_to_date() -> None:
    assert SNAPSHOT.exists(), "run `make openapi` to create apps/api/openapi.json"
    committed = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert app.openapi() == committed, (
        "API changed but openapi.json is stale: run `make openapi` (regenerates the web "
        "client too) and review the diff for breaking changes."
    )
