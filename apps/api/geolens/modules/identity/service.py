import uuid
from decimal import Decimal
from typing import Any

from geolens.core.config import get_settings
from geolens.core.db import session_scope
from geolens.modules.identity.models import UsageLedger, Workspace
from geolens.modules.identity.repository import UsageRepository, WorkspaceDirectory

_default_workspace_id: uuid.UUID | None = None


def ensure_default_workspace() -> uuid.UUID:
    global _default_workspace_id
    if _default_workspace_id is None:
        slug = get_settings().default_workspace_slug
        with session_scope() as s:
            directory = WorkspaceDirectory(s)
            ws = directory.by_slug(slug) or directory.add(Workspace(slug=slug, name="Default"))
            _default_workspace_id = ws.id
    return _default_workspace_id


def record_usage(
    kind: str, units: int = 1, cost_usd: Decimal = Decimal(0), meta: dict[str, Any] | None = None
) -> None:
    with session_scope() as s:
        UsageRepository(s).add(
            UsageLedger(kind=kind, units=units, cost_usd=cost_usd, meta=meta or {})
        )
