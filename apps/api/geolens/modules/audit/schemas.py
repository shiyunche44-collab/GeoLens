import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class AuditCreate(BaseModel):
    url: HttpUrl
    project_id: uuid.UUID | None = None


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: str
    category: str
    severity: str
    message: str
    recommendation: str | None


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID | None
    url: str
    status: str
    score: int | None
    error: str | None
    created_at: datetime
    finished_at: datetime | None
    findings: list[FindingOut]
