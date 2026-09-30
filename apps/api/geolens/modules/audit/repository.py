from collections.abc import Sequence

from geolens.core.repository import WorkspaceRepository
from geolens.modules.audit.models import AuditJob


class AuditJobRepository(WorkspaceRepository[AuditJob]):
    model = AuditJob

    def recent(self, limit: int = 50) -> Sequence[AuditJob]:
        stmt = self.select().order_by(AuditJob.created_at.desc()).limit(limit)
        return self.session.scalars(stmt).all()
