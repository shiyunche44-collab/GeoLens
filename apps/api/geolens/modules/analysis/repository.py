import uuid
from collections.abc import Sequence

from sqlalchemy import delete

from geolens.core.repository import WorkspaceRepository
from geolens.core.tenancy import current_workspace_id
from geolens.modules.analysis.models import AnalyzedResponse, Citation, Mention


class AnalyzedResponseRepository(WorkspaceRepository[AnalyzedResponse]):
    model = AnalyzedResponse

    def delete_for_response(self, response_id: uuid.UUID) -> None:
        self.session.execute(
            delete(AnalyzedResponse).where(
                AnalyzedResponse.response_id == response_id,
                AnalyzedResponse.workspace_id == current_workspace_id(),
            )
        )

    def for_project(self, project_id: uuid.UUID) -> Sequence[AnalyzedResponse]:
        stmt = self.select().where(AnalyzedResponse.project_id == project_id)
        return self.session.scalars(stmt).all()


class MentionRepository(WorkspaceRepository[Mention]):
    model = Mention

    def for_analyses(self, ids: list[uuid.UUID]) -> Sequence[Mention]:
        return self.session.scalars(self.select().where(Mention.analysis_id.in_(ids))).all()


class CitationRepository(WorkspaceRepository[Citation]):
    model = Citation

    def for_analyses(self, ids: list[uuid.UUID]) -> Sequence[Citation]:
        return self.session.scalars(self.select().where(Citation.analysis_id.in_(ids))).all()
