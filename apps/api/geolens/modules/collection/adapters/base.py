"""Engine adapter contract (ADR-0005).

An adapter knows how to ask ONE generative engine a question and how to turn
that engine's raw payload into a ``ParsedAnswer``. Everything downstream
(analysis, metrics) is engine-agnostic.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal, Protocol, runtime_checkable

Region = Literal["cn", "global"]
Mode = Literal["api", "browser", "serp", "mock"]
# How close the answer is to what a real user sees in the product UI.
Fidelity = Literal["ui", "api_search", "api_no_search", "synthetic"]


@dataclass(frozen=True)
class QueryRequest:
    prompt: str
    locale: str = "zh-CN"
    sample_idx: int = 0


@dataclass(frozen=True)
class RawResponse:
    """Exactly what the engine returned. Persisted verbatim as the raw snapshot."""

    engine_id: str
    payload: dict[str, Any]
    model: str | None = None
    latency_ms: int = 0
    units: int = 0  # tokens / credits consumed, for the usage ledger
    cost_usd: Decimal = Decimal(0)


@dataclass(frozen=True)
class CitationRef:
    url: str
    title: str | None = None


@dataclass(frozen=True)
class ParsedAnswer:
    text: str
    citations: list[CitationRef] = field(default_factory=list[CitationRef])
    model: str | None = None


@runtime_checkable
class EngineAdapter(Protocol):
    engine_id: str
    display_name: str
    region: Region
    mode: Mode
    fidelity: Fidelity

    async def query(self, req: QueryRequest) -> RawResponse: ...

    def parse(self, raw: RawResponse) -> ParsedAnswer: ...
