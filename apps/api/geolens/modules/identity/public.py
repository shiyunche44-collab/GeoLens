"""Public interface of the identity module. Other modules import ONLY this file."""

import uuid
from decimal import Decimal
from typing import Any

from fastapi import Header

from geolens.core.tenancy import set_workspace
from geolens.modules.identity import service


def ensure_default_workspace() -> uuid.UUID:
    return service.ensure_default_workspace()


def record_usage(
    kind: str, units: int = 1, cost_usd: Decimal = Decimal(0), meta: dict[str, Any] | None = None
) -> None:
    """Meter an external call against the current workspace (ADR: cost is first-class)."""
    service.record_usage(kind, units, cost_usd, meta)


async def workspace_scope(x_workspace_id: uuid.UUID | None = Header(default=None)) -> None:
    """FastAPI dependency: put the request's workspace into the tenant context.

    MVP is single-tenant: without the header the default workspace is used.
    P2 replaces this with auth-derived membership checks.
    """
    set_workspace(x_workspace_id or service.ensure_default_workspace())
