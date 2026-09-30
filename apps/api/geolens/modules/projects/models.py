import uuid

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from geolens.core.db import Base, TimestampMixin
from geolens.core.tenancy import WorkspaceScopedMixin


class Project(WorkspaceScopedMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    primary_domain: Mapped[str | None] = mapped_column(String(255))
    default_locale: Mapped[str] = mapped_column(String(16), default="zh-CN")

    brands: Mapped[list["Brand"]] = relationship(back_populates="project", lazy="selectin")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="project", lazy="selectin")


class Brand(WorkspaceScopedMixin, TimestampMixin, Base):
    """Own brand (is_competitor=False) or a competitor to benchmark against."""

    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_competitor: Mapped[bool] = mapped_column(Boolean, default=False)

    project: Mapped[Project] = relationship(back_populates="brands")


class Prompt(WorkspaceScopedMixin, TimestampMixin, Base):
    """A question real users ask AI engines, e.g. "最好的 GEO 分析工具有哪些？"."""

    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    topic: Mapped[str | None] = mapped_column(String(100))
    locale: Mapped[str | None] = mapped_column(String(16))

    project: Mapped[Project] = relationship(back_populates="prompts")
