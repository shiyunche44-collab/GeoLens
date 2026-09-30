"""Pure, engine-agnostic answer analysis. No DB, no network — trivially testable
and re-runnable over raw snapshots (ADR-0003).

Bump ANALYZER_VERSION whenever a step changes its output; facts are stored with
the version that produced them so history can be recomputed.
"""

import uuid
from dataclasses import dataclass, field

ANALYZER_VERSION = "2026.09.1"


@dataclass(frozen=True)
class BrandRef:
    id: uuid.UUID
    name: str
    aliases: list[str] = field(default_factory=list[str])
    domains: list[str] = field(default_factory=list[str])
    is_competitor: bool = False


@dataclass(frozen=True)
class AnalysisInput:
    text: str
    citation_urls: list[str]
    brands: list[BrandRef]


@dataclass(frozen=True)
class MentionFact:
    brand_id: uuid.UUID
    position: int  # 1 = first brand mentioned in the answer
    snippet: str


@dataclass(frozen=True)
class CitationFact:
    url: str
    domain: str
    position: int  # 1 = first cited source
    brand_id: uuid.UUID | None  # set when the domain belongs to a tracked brand


@dataclass(frozen=True)
class AnalysisResult:
    mentions: list[MentionFact]
    citations: list[CitationFact]
    analyzer_version: str = ANALYZER_VERSION
