"""Fact tables. Append-only per analyzer_version; shaped for a later ClickHouse move."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from geolens.core.db import Base, TimestampMixin
from geolens.core.tenancy import WorkspaceScopedMixin


class AnalyzedResponse(WorkspaceScopedMixin, TimestampMixin, Base):
    """Header fact: one row per analyzed response (the denominator for rates)."""

    __tablename__ = "analyzed_responses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    response_id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    run_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    engine_id: Mapped[str] = mapped_column(String(64))
    collected_on: Mapped[date] = mapped_column(Date, index=True)
    analyzer_version: Mapped[str] = mapped_column(String(32))


class Mention(WorkspaceScopedMixin, TimestampMixin, Base):
    __tablename__ = "mentions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyzed_responses.id", ondelete="CASCADE"), index=True
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    position: Mapped[int] = mapped_column(Integer)
    snippet: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[float | None] = mapped_column()  # P1 next: LLM judge, -1..1
    analyzer_version: Mapped[str] = mapped_column(String(32))


class Citation(WorkspaceScopedMixin, TimestampMixin, Base):
    __tablename__ = "citations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyzed_responses.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(2048))
    domain: Mapped[str] = mapped_column(String(255), index=True)
    position: Mapped[int] = mapped_column(Integer)
    brand_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    analyzer_version: Mapped[str] = mapped_column(String(32))
