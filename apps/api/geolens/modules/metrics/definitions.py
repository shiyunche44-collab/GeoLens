"""THE single source of truth for GEO metric definitions (指标口径).

Everything here is pure and additive-first: we store additive counts
(``BrandCounts``) and derive ratios on read, so any time window or engine
grouping can be aggregated correctly. Changing a formula = update the golden
tests in tests/golden/ + write an ADR.
"""

import math
import uuid
from collections.abc import Iterable
from dataclasses import dataclass

# Composite visibility score weights (must sum to 1).
SCORE_WEIGHTS: dict[str, float] = {
    "mention_rate": 0.4,
    "share_of_voice": 0.3,
    "position": 0.2,
    "citation_rate": 0.1,
}


@dataclass(frozen=True)
class Observation:
    """One analyzed answer."""

    mention_positions: dict[uuid.UUID, int]
    cited_brand_ids: frozenset[uuid.UUID]


@dataclass(frozen=True)
class BrandCounts:
    n_responses: int = 0  # answers observed
    n_mentioned: int = 0  # answers mentioning the brand
    n_cited: int = 0  # answers citing one of the brand's domains
    position_sum: int = 0  # sum of positions over answers mentioning the brand
    total_brand_mentions: int = 0  # Σ over tracked brands of answers mentioning them

    def __add__(self, other: "BrandCounts") -> "BrandCounts":
        return BrandCounts(
            self.n_responses + other.n_responses,
            self.n_mentioned + other.n_mentioned,
            self.n_cited + other.n_cited,
            self.position_sum + other.position_sum,
            self.total_brand_mentions + other.total_brand_mentions,
        )


@dataclass(frozen=True)
class Ratio:
    value: float
    n: int
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class BrandMetrics:
    mention_rate: Ratio
    share_of_voice: float | None
    avg_position: float | None
    citation_rate: Ratio
    visibility_score: float


def wilson(successes: int, n: int, z: float = 1.96) -> Ratio:
    """Proportion with a Wilson 95% interval — LLM answers are samples, not facts."""
    if n == 0:
        return Ratio(0.0, 0, 0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return Ratio(
        round(p, 6), n, round(max(0.0, centre - half), 6), round(min(1.0, centre + half), 6)
    )


def count(observations: Iterable[Observation], brand_id: uuid.UUID) -> BrandCounts:
    n = mentioned = cited = pos_sum = total = 0
    for o in observations:
        n += 1
        total += len(o.mention_positions)
        if brand_id in o.mention_positions:
            mentioned += 1
            pos_sum += o.mention_positions[brand_id]
        if brand_id in o.cited_brand_ids:
            cited += 1
    return BrandCounts(n, mentioned, cited, pos_sum, total)


def derive(c: BrandCounts) -> BrandMetrics:
    mention_rate = wilson(c.n_mentioned, c.n_responses)
    citation_rate = wilson(c.n_cited, c.n_responses)
    sov = c.n_mentioned / c.total_brand_mentions if c.total_brand_mentions else None
    avg_pos = c.position_sum / c.n_mentioned if c.n_mentioned else None
    position_score = 1 / avg_pos if avg_pos else 0.0
    score = 100 * (
        SCORE_WEIGHTS["mention_rate"] * mention_rate.value
        + SCORE_WEIGHTS["share_of_voice"] * (sov or 0.0)
        + SCORE_WEIGHTS["position"] * position_score
        + SCORE_WEIGHTS["citation_rate"] * citation_rate.value
    )
    return BrandMetrics(
        mention_rate=mention_rate,
        share_of_voice=round(sov, 6) if sov is not None else None,
        avg_position=round(avg_pos, 4) if avg_pos is not None else None,
        citation_rate=citation_rate,
        visibility_score=round(score, 2),
    )
