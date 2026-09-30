import uuid
from datetime import date

from pydantic import BaseModel


class ResponseFacts(BaseModel):
    """Per-response observation handed to metrics via public.py."""

    response_id: uuid.UUID
    engine_id: str
    collected_on: date
    mention_positions: dict[uuid.UUID, int]  # brand_id -> position
    cited_brand_ids: list[uuid.UUID]
