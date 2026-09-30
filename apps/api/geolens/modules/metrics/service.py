import uuid
from collections import defaultdict
from datetime import date

from geolens.core.db import session_scope
from geolens.modules.analysis import public as analysis
from geolens.modules.metrics import definitions as d
from geolens.modules.metrics.models import MetricDaily
from geolens.modules.metrics.repository import MetricDailyRepository
from geolens.modules.metrics.schemas import (
    BrandMetricsOut,
    DailyPointOut,
    ProjectMetricsOut,
    RatioOut,
)
from geolens.modules.projects import public as projects

RECOMPUTE_TASK = "metrics.recompute_project"
ALL_ENGINES = "all"


def recompute_project(project_id: uuid.UUID) -> None:
    """Rebuild metric_daily for a project from analysis facts (idempotent)."""
    snapshot = projects.get_snapshot(project_id)
    with session_scope() as s:
        repo = MetricDailyRepository(s)
        repo.lock_project(project_id)  # read facts only after we own the lock
        facts = analysis.list_response_facts(project_id)
        groups: dict[tuple[str, date], list[d.Observation]] = defaultdict(list)
        for f in facts:
            obs = d.Observation(f.mention_positions, frozenset(f.cited_brand_ids))
            groups[(f.engine_id, f.collected_on)].append(obs)
        rows = [
            MetricDaily(
                project_id=project_id,
                brand_id=b.id,
                engine_id=engine,
                day=day,
                **d.count(obs, b.id).__dict__,
            )
            for (engine, day), obs in groups.items()
            for b in snapshot.brands
        ]
        repo.replace_project(project_id, rows)


def _out(counts: d.BrandCounts) -> dict[str, object]:
    m = d.derive(counts)
    return {
        "mention_rate": RatioOut(**m.mention_rate.__dict__),
        "share_of_voice": m.share_of_voice,
        "avg_position": m.avg_position,
        "citation_rate": RatioOut(**m.citation_rate.__dict__),
        "visibility_score": m.visibility_score,
    }


def _counts(row: MetricDaily) -> d.BrandCounts:
    return d.BrandCounts(
        row.n_responses, row.n_mentioned, row.n_cited, row.position_sum, row.total_brand_mentions
    )


def get_project_metrics(project_id: uuid.UUID) -> ProjectMetricsOut:
    snapshot = projects.get_snapshot(project_id)
    brands = {b.id: b for b in snapshot.brands}
    with session_scope() as s:
        rows = MetricDailyRepository(s).for_project(project_id)
        by_brand_engine: dict[tuple[uuid.UUID, str], d.BrandCounts] = defaultdict(d.BrandCounts)
        by_brand_day: dict[tuple[uuid.UUID, date], d.BrandCounts] = defaultdict(d.BrandCounts)
        for r in rows:
            c = _counts(r)
            by_brand_engine[(r.brand_id, r.engine_id)] += c
            by_brand_engine[(r.brand_id, ALL_ENGINES)] += c
            by_brand_day[(r.brand_id, r.day)] += c

    def meta(bid: uuid.UUID) -> dict[str, object]:
        return {
            "brand_id": bid,
            "brand_name": brands[bid].name,
            "is_competitor": brands[bid].is_competitor,
        }

    summary = [
        BrandMetricsOut(**meta(bid), engine_id=engine, **_out(c))  # type: ignore[arg-type]
        for (bid, engine), c in sorted(by_brand_engine.items(), key=lambda kv: str(kv[0]))
        if bid in brands
    ]
    daily = [
        DailyPointOut(**meta(bid), engine_id=ALL_ENGINES, day=day, **_out(c))  # type: ignore[arg-type]
        for (bid, day), c in sorted(by_brand_day.items(), key=lambda kv: (kv[0][1], str(kv[0][0])))
        if bid in brands
    ]
    return ProjectMetricsOut(project_id=project_id, summary=summary, daily=daily)
