"""Tenant context. Every business row carries ``workspace_id`` (see ADR-0006).

The current workspace lives in a ContextVar that the HTTP layer and Celery tasks
set; repositories read it and refuse to run without it.
"""

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

_current_workspace: ContextVar[uuid.UUID | None] = ContextVar("geolens_workspace", default=None)


class MissingTenantContextError(RuntimeError):
    pass


def current_workspace_id() -> uuid.UUID:
    ws = _current_workspace.get()
    if ws is None:
        raise MissingTenantContextError(
            "No workspace in context. Wrap the call in workspace_context(...) "
            "or go through the HTTP/task entrypoints that set it."
        )
    return ws


def set_workspace(workspace_id: uuid.UUID) -> None:
    _current_workspace.set(workspace_id)


@contextmanager
def workspace_context(workspace_id: uuid.UUID) -> Generator[None]:
    token = _current_workspace.set(workspace_id)
    try:
        yield
    finally:
        _current_workspace.reset(token)


class WorkspaceScopedMixin:
    """Mix into every business table. Cross-module references are plain UUIDs (no FK)."""

    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
