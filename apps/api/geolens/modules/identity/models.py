import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from geolens.core.db import Base, TimestampMixin
from geolens.core.tenancy import WorkspaceScopedMixin


class Workspace(TimestampMixin, Base):
    """Tenant root. Global table (no workspace_id)."""

    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    plan: Mapped[str] = mapped_column(String(32), default="self_hosted")


class UsageLedger(WorkspaceScopedMixin, TimestampMixin, Base):
    """Every metered external call (LLM, SERP, crawl) lands here. Future billing source."""

    __tablename__ = "usage_ledger"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(64))  # e.g. "engine_query:deepseek"
    units: Mapped[int] = mapped_column(default=1)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal(0))
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
