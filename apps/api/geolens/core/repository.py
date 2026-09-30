import uuid
from collections.abc import Sequence
from typing import Any, ClassVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from geolens.core.tenancy import WorkspaceScopedMixin, current_workspace_id


class WorkspaceRepository[M: WorkspaceScopedMixin]:
    """Base repository: every query is filtered by the current workspace.

    Subclasses set ``model``. Never query a WorkspaceScoped table without going
    through a repository — that is how tenant isolation stays enforced.
    """

    model: ClassVar[type[Any]]

    def __init__(self, session: Session) -> None:
        self.session = session

    def select(self) -> Select[M]:
        return select(self.model).where(self.model.workspace_id == current_workspace_id())

    def get(self, obj_id: uuid.UUID) -> M | None:
        return self.session.scalars(self.select().where(self.model.id == obj_id)).first()

    def list(self) -> Sequence[M]:
        return self.session.scalars(self.select()).all()

    def add(self, obj: M) -> M:
        obj.workspace_id = current_workspace_id()
        self.session.add(obj)
        self.session.flush()
        return obj
