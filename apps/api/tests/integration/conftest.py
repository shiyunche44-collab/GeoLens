import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from geolens.core.db import Base, get_engine

API_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def migrated_db() -> None:
    """Apply the real migrations (so they are tested too); skip if Postgres is absent."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("select 1"))
    except OperationalError:
        if os.environ.get("CI"):  # never let CI go green by silently skipping these
            pytest.fail("PostgreSQL not reachable in CI (check GEOLENS_DATABASE_URL)")
        pytest.skip("PostgreSQL not reachable (set GEOLENS_DATABASE_URL)")
    with get_engine().begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    cfg = Config(str(API_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_ROOT / "migrations"))
    command.upgrade(cfg, "head")


@pytest.fixture
def client(migrated_db: None) -> Iterator[TestClient]:
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with get_engine().begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} CASCADE"))
    import geolens.modules.identity.service as identity_service

    identity_service._default_workspace_id = None  # re-seed after truncate
    from geolens.app.main import app

    with TestClient(app) as c:
        yield c
