import json
import uuid
from pathlib import Path

import pytest

from geolens.modules.metrics import definitions as d

CASE = json.loads((Path(__file__).parent / "metrics_cases.json").read_text(encoding="utf-8"))
IDS = {key: uuid.uuid5(uuid.NAMESPACE_URL, key) for key in CASE["brands"]}
OBS = [
    d.Observation(
        {IDS[k]: p for k, p in o["mentions"].items()}, frozenset(IDS[k] for k in o["cited"])
    )
    for o in CASE["observations"]
]


@pytest.mark.parametrize("brand", CASE["brands"])
def test_metric_definitions_match_golden(brand: str) -> None:
    exp = CASE["expected"][brand]
    counts = d.count(OBS, IDS[brand])
    assert counts.__dict__ == exp["counts"]
    m = d.derive(counts)
    for ratio in ("mention_rate", "citation_rate"):
        assert getattr(m, ratio).__dict__ == pytest.approx(exp[ratio], abs=1e-4)
    assert m.share_of_voice == pytest.approx(exp["share_of_voice"])
    assert m.avg_position == pytest.approx(exp["avg_position"])
    assert m.visibility_score == pytest.approx(exp["visibility_score"], abs=0.01)


@pytest.mark.parametrize("brand", CASE["brands"])
def test_counts_are_additive(brand: str) -> None:
    """Storing counts (not ratios) is what lets any window/engine be aggregated."""
    bid = IDS[brand]
    assert d.count(OBS[:2], bid) + d.count(OBS[2:], bid) == d.count(OBS, bid)


def test_empty_window() -> None:
    m = d.derive(d.BrandCounts())
    assert (m.mention_rate.n, m.share_of_voice, m.avg_position, m.visibility_score) == (
        0,
        None,
        None,
        0.0,
    )


def test_score_weights_sum_to_one() -> None:
    assert sum(d.SCORE_WEIGHTS.values()) == pytest.approx(1.0)
