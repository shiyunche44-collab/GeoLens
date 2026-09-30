import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from geolens.core.db import Base, TimestampMixin
from geolens.core.tenancy import WorkspaceScopedMixin


class Run(WorkspaceScopedMixin, TimestampMixin, Base):
    """One execution of a project's prompt set across engines."""

    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)  # cross-module: no FK
    trigger: Mapped[str] = mapped_column(String(16), default="manual")  # manual | schedule
    status: Mapped[str] = mapped_column(String(16), default="pending")
    engines: Mapped[list[str]] = mapped_column(JSON)
    samples_per_prompt: Mapped[int] = mapped_column(Integer)
    total_tasks: Mapped[int] = mapped_column(Integer, default=0)
    done_tasks: Mapped[int] = mapped_column(Integer, default=0)
    failed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class QueryTask(WorkspaceScopedMixin, TimestampMixin, Base):
    """prompt × engine × sample. The unit of work sent to a collector queue."""

    __tablename__ = "query_tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"), index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    prompt_text: Mapped[str] = mapped_column(Text)  # frozen copy: prompts may be edited later
    engine_id: Mapped[str] = mapped_column(String(64))
    locale: Mapped[str] = mapped_column(String(16))
    sample_idx: Mapped[int] = mapped_column(Integer)
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|done|failed
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    # Set as soon as the raw answer is stored, so a failed parse can be reprocessed later.
    raw_uri: Mapped[str | None] = mapped_column(String(1024))


class Response(WorkspaceScopedMixin, TimestampMixin, Base):
    """A collected answer. ``raw_uri`` points at the immutable raw snapshot (ADR-0003)."""

    __tablename__ = "responses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("query_tasks.id"), unique=True)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"), index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    engine_id: Mapped[str] = mapped_column(String(64))
    fidelity: Mapped[str] = mapped_column(String(32))
    model: Mapped[str | None] = mapped_column(String(128))
    raw_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
