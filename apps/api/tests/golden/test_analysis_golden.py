"""Re-analysis from raw snapshots is deterministic (ADR-0003): recorded engine
payload → adapter.parse → pipeline.analyze → exactly these facts."""

import json
import uuid
from pathlib import Path
from typing import Any

import pytest

from geolens.modules.analysis.pipeline import ANALYZER_VERSION, AnalysisInput, BrandRef, analyze
from geolens.modules.collection.adapters import registry
from geolens.modules.collection.adapters.base import RawResponse

HERE = Path(__file__).parent
GOLDEN: dict[str, Any] = json.loads((HERE / "analysis_cases.json").read_text(encoding="utf-8"))
ENGINE_FIXTURES = HERE.parent / "fixtures" / "engines"
BRANDS = [
    BrandRef(
        id=uuid.uuid5(uuid.NAMESPACE_URL, b["key"]),
        name=b["name"],
        aliases=b.get("aliases", []),
        domains=b.get("domains", []),
        is_competitor=b.get("is_competitor", False),
    )
    for b in GOLDEN["brands"]
]
KEY_BY_ID = {uuid.uuid5(uuid.NAMESPACE_URL, b["key"]): b["key"] for b in GOLDEN["brands"]}


def test_golden_file_matches_analyzer_version() -> None:
    assert GOLDEN["analyzer_version"] == ANALYZER_VERSION, (
        "Analyzer version changed: re-derive analysis_cases.json expectations and update its "
        "analyzer_version (or revert the version bump)."
    )


@pytest.mark.parametrize("case", GOLDEN["from_raw_snapshot"], ids=lambda c: c["engine"])
def test_reanalysis_from_raw_snapshot(case: dict[str, Any]) -> None:
    fixture = json.loads((ENGINE_FIXTURES / f"{case['engine']}.json").read_text("utf-8"))
    adapter = registry.get(case["engine"])
    parsed = adapter.parse(RawResponse(engine_id=case["engine"], payload=fixture["response"]))

    result = analyze(
        AnalysisInput(
            text=parsed.text, citation_urls=[c.url for c in parsed.citations], brands=BRANDS
        )
    )

    assert [[KEY_BY_ID[m.brand_id], m.position] for m in result.mentions] == case["mentions"]
    got = [
        [c.url, c.domain, c.position, KEY_BY_ID.get(c.brand_id) if c.brand_id else None]
        for c in result.citations
    ]
    assert got == case["citations"]
    assert result.analyzer_version == ANALYZER_VERSION
