from geolens.modules.analysis.pipeline.base import (
    ANALYZER_VERSION,
    AnalysisInput,
    AnalysisResult,
    BrandRef,
    CitationFact,
    MentionFact,
)
from geolens.modules.analysis.pipeline.steps import extract_citations, match_brands

__all__ = [
    "ANALYZER_VERSION",
    "AnalysisInput",
    "AnalysisResult",
    "BrandRef",
    "CitationFact",
    "MentionFact",
    "analyze",
]


def analyze(inp: AnalysisInput) -> AnalysisResult:
    """Run every analysis step. P1 next: LLM-judged sentiment + list-position steps."""
    return AnalysisResult(
        mentions=match_brands(inp.text, inp.brands),
        citations=extract_citations(inp.citation_urls, inp.brands),
    )
