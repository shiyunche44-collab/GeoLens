from sqlalchemy import select
from sqlalchemy.orm import Session

from geolens.core.repository import WorkspaceRepository
from geolens.modules.identity.models import UsageLedger, Workspace


class WorkspaceDirectory:
    """Workspaces are the tenant root, so this is not workspace-filtered."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def by_slug(self, slug: str) -> Workspace | None:
        return self.session.scalars(select(Workspace).where(Workspace.slug == slug)).first()

    def add(self, ws: Workspace) -> Workspace:
        self.session.add(ws)
        self.session.flush()
        return ws


class UsageRepository(WorkspaceRepository[UsageLedger]):
    model = UsageLedger
