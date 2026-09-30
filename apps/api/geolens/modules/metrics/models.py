import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from geolens.core.db import Base, TimestampMixin
from geolens.core.tenancy import WorkspaceScopedMixin


class MetricDaily(WorkspaceScopedMixin, TimestampMixin, Base):
    """Additive counts per project × brand × engine × day. Ratios are derived on read."""

    __tablename__ = "metric_daily"
    __table_args__ = (UniqueConstraint("project_id", "brand_id", "engine_id", "day"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    brand_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    engine_id: Mapped[str] = mapped_column(String(64))
    day: Mapped[date] = mapped_column(Date)
    n_responses: Mapped[int] = mapped_column(Integer)
    n_mentioned: Mapped[int] = mapped_column(Integer)
    n_cited: Mapped[int] = mapped_column(Integer)
    position_sum: Mapped[int] = mapped_column(Integer)
    total_brand_mentions: Mapped[int] = mapped_column(Integer)
