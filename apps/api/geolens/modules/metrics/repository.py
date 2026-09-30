import uuid
from collections.abc import Sequence

from sqlalchemy import delete, func, select

from geolens.core.repository import WorkspaceRepository
from geolens.core.tenancy import current_workspace_id
from geolens.modules.metrics.models import MetricDaily


class MetricDailyRepository(WorkspaceRepository[MetricDaily]):
    model = MetricDaily

    def lock_project(self, project_id: uuid.UUID) -> None:
        """Serialize recomputes of one project (transaction-scoped advisory lock)."""
        self.session.execute(select(func.pg_advisory_xact_lock(func.hashtext(str(project_id)))))

    def replace_project(self, project_id: uuid.UUID, rows: list[MetricDaily]) -> None:
        self.session.execute(
            delete(MetricDaily).where(
                MetricDaily.project_id == project_id,
                MetricDaily.workspace_id == current_workspace_id(),
            )
        )
        for r in rows:
            self.add(r)

    def for_project(self, project_id: uuid.UUID) -> Sequence[MetricDaily]:
        stmt = self.select().where(MetricDaily.project_id == project_id).order_by(MetricDaily.day)
        return self.session.scalars(stmt).all()
