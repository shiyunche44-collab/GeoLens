import uuid
from collections import defaultdict

from geolens.core import events
from geolens.core.db import session_scope
from geolens.core.tenancy import current_workspace_id
from geolens.modules.analysis.events import RESPONSE_ANALYZED
from geolens.modules.analysis.models import AnalyzedResponse, Citation, Mention
from geolens.modules.analysis.pipeline import ANALYZER_VERSION, AnalysisInput, BrandRef, analyze
from geolens.modules.analysis.repository import (
    AnalyzedResponseRepository,
    CitationRepository,
    MentionRepository,
)
from geolens.modules.analysis.schemas import ResponseFacts
from geolens.modules.collection import public as collection
from geolens.modules.projects import public as projects

ANALYZE_TASK = "analysis.analyze_response"


def analyze_response(response_id: uuid.UUID) -> None:
    """Idempotent: re-analyzing replaces the previous facts for this response."""
    resp = collection.get_response(response_id)
    snapshot = projects.get_snapshot(resp.project_id)
    brands = [
        BrandRef(
            id=b.id,
            name=b.name,
            aliases=b.aliases,
            domains=b.domains,
            is_competitor=b.is_competitor,
        )
        for b in snapshot.brands
    ]
    result = analyze(
        AnalysisInput(
            text=resp.answer_text, citation_urls=[c.url for c in resp.citations], brands=brands
        )
    )
    with session_scope() as s:
        headers = AnalyzedResponseRepository(s)
        headers.delete_for_response(response_id)
        header = headers.add(
            AnalyzedResponse(
                response_id=response_id,
                project_id=resp.project_id,
                run_id=resp.run_id,
                engine_id=resp.engine_id,
                collected_on=resp.created_at.date(),
                analyzer_version=ANALYZER_VERSION,
            )
        )
        mentions, citations = MentionRepository(s), CitationRepository(s)
        for m in result.mentions:
            mentions.add(
                Mention(
                    analysis_id=header.id,
                    brand_id=m.brand_id,
                    position=m.position,
                    snippet=m.snippet,
                    analyzer_version=result.analyzer_version,
                )
            )
        for c in result.citations:
            citations.add(
                Citation(
                    analysis_id=header.id,
                    url=c.url,
                    domain=c.domain,
                    position=c.position,
                    brand_id=c.brand_id,
                    analyzer_version=result.analyzer_version,
                )
            )
    events.publish(
        RESPONSE_ANALYZED,
        workspace_id=current_workspace_id(),
        response_id=str(response_id),
        project_id=str(resp.project_id),
    )


def list_response_facts(project_id: uuid.UUID) -> list[ResponseFacts]:
    with session_scope() as s:
        headers = AnalyzedResponseRepository(s).for_project(project_id)
        ids = [h.id for h in headers]
        positions: dict[uuid.UUID, dict[uuid.UUID, int]] = defaultdict(dict)
        for m in MentionRepository(s).for_analyses(ids):
            positions[m.analysis_id][m.brand_id] = m.position
        cited: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
        for c in CitationRepository(s).for_analyses(ids):
            if c.brand_id is not None:
                cited[c.analysis_id].add(c.brand_id)
        return [
            ResponseFacts(
                response_id=h.response_id,
                engine_id=h.engine_id,
                collected_on=h.collected_on,
                mention_positions=positions[h.id],
                cited_brand_ids=sorted(cited[h.id]),
            )
            for h in headers
        ]
