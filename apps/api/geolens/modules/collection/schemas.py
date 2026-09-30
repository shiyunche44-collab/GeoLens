import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EngineOut(BaseModel):
    id: str
    display_name: str
    region: str
    mode: str
    fidelity: str


class RunCreate(BaseModel):
    engines: list[str] = Field(min_length=1)
    samples_per_prompt: int | None = Field(default=None, ge=1, le=20)


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    engines: list[str]
    samples_per_prompt: int
    total_tasks: int
    done_tasks: int
    failed_tasks: int
    created_at: datetime
    finished_at: datetime | None


class CitationOut(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    url: str
    title: str | None = None


class ResponseOut(BaseModel):
    """Also the DTO other modules receive via public.get_response()."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    project_id: uuid.UUID
    prompt_id: uuid.UUID
    engine_id: str
    fidelity: str
    model: str | None
    answer_text: str
    citations: list[CitationOut]
    created_at: datetime
