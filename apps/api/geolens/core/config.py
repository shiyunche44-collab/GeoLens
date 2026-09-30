import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ROOT = Path(__file__).resolve().parents[2]  # apps/api (or /app in the image)
# Repo root = the directory holding apps/api; falls back to the API root in containers.
_REPO_ROOT = next((p for p in _API_ROOT.parents if (p / "apps" / "api").is_dir()), _API_ROOT)

# Engine credentials (DEEPSEEK_API_KEY, ...) are read from the process env by the
# adapters, so export the repo .env there too. Tests stay hermetic.
if os.environ.get("GEOLENS_ENV") != "test":
    load_dotenv(_REPO_ROOT / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_prefix="GEOLENS_",
        extra="ignore",
    )

    env: Literal["dev", "test", "prod"] = "dev"
    database_url: str = "postgresql+psycopg://geolens:geolens@localhost:5432/geolens"
    redis_url: str = "redis://localhost:6379/0"

    # Run Celery tasks inline (tests, local demos without a worker).
    celery_eager: bool = False

    storage_backend: Literal["local", "s3"] = "local"
    storage_local_dir: str = str(_REPO_ROOT / ".data" / "objects")
    s3_bucket: str = "geolens-raw"
    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str = "us-east-1"

    # Single-tenant MVP: requests without X-Workspace-Id use this workspace.
    default_workspace_slug: str = "default"

    # Audit crawler SSRF guard. Only enable for local development.
    audit_allow_private_hosts: bool = False

    # Collection defaults
    default_samples_per_prompt: int = 3
    http_timeout_seconds: float = 60.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
