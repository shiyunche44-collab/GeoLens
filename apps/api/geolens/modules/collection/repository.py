import uuid
from collections.abc import Sequence

from sqlalchemy import update

from geolens.core.repository import WorkspaceRepository
from geolens.core.tenancy import current_workspace_id
from geolens.modules.collection.models import QueryTask, Response, Run


class RunRepository(WorkspaceRepository[Run]):
    model = Run

    def bump(self, run_id: uuid.UUID, *, failed: bool) -> Run:
        """Atomically count a finished task; returns the refreshed run."""
        column = Run.failed_tasks if failed else Run.done_tasks
        self.session.execute(
            update(Run)
            .where(Run.id == run_id, Run.workspace_id == current_workspace_id())
            .values({column: column + 1})
        )
        run = self.get(run_id)
        assert run is not None
        self.session.refresh(run)
        return run


class QueryTaskRepository(WorkspaceRepository[QueryTask]):
    model = QueryTask

    def existing_keys(self, keys: list[str]) -> set[str]:
        stmt = self.select().where(QueryTask.idempotency_key.in_(keys))
        return {t.idempotency_key for t in self.session.scalars(stmt)}


class ResponseRepository(WorkspaceRepository[Response]):
    model = Response

    def for_run(self, run_id: uuid.UUID) -> Sequence[Response]:
        return self.session.scalars(self.select().where(Response.run_id == run_id)).all()
