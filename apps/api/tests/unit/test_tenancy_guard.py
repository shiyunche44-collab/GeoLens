import uuid
from typing import Any, cast

import pytest

from geolens.core.tenancy import MissingTenantContextError, current_workspace_id, workspace_context
from geolens.modules.projects.repository import ProjectRepository


def test_repository_refuses_to_query_without_tenant_context() -> None:
    repo = ProjectRepository(cast(Any, None))  # never reaches the DB
    with pytest.raises(MissingTenantContextError):
        repo.select()


def test_context_is_scoped() -> None:
    ws = uuid.uuid4()
    with workspace_context(ws):
        assert current_workspace_id() == ws
    with pytest.raises(MissingTenantContextError):
        current_workspace_id()
