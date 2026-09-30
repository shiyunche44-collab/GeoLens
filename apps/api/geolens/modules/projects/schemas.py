import uuid

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    primary_domain: str | None = None
    default_locale: str = "zh-CN"


class BrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    aliases: list[str] = []
    domains: list[str] = []
    is_competitor: bool = False


class PromptCreate(BaseModel):
    text: str = Field(min_length=1)
    topic: str | None = None
    locale: str | None = None


class BrandOut(BrandCreate):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )
    id: uuid.UUID


class PromptOut(PromptCreate):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )
    id: uuid.UUID


class ProjectOut(ProjectCreate):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )
    id: uuid.UUID
    brands: list[BrandOut] = []
    prompts: list[PromptOut] = []


class ProjectSnapshot(BaseModel):
    """Read model handed to other modules via public.py (no ORM objects cross modules)."""

    id: uuid.UUID
    name: str
    default_locale: str
    brands: list[BrandOut]
    prompts: list[PromptOut]
