import uuid
from datetime import date

from pydantic import BaseModel


class RatioOut(BaseModel):
    value: float
    n: int
    ci_low: float
    ci_high: float


class BrandMetricsOut(BaseModel):
    brand_id: uuid.UUID
    brand_name: str
    is_competitor: bool
    engine_id: str  # "all" = every engine combined
    mention_rate: RatioOut
    share_of_voice: float | None
    avg_position: float | None
    citation_rate: RatioOut
    visibility_score: float


class DailyPointOut(BrandMetricsOut):
    day: date


class ProjectMetricsOut(BaseModel):
    project_id: uuid.UUID
    summary: list[BrandMetricsOut]  # whole window, per brand × engine (incl. "all")
    daily: list[DailyPointOut]  # engine="all" time series
