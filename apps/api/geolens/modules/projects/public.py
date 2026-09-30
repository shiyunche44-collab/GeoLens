"""Public interface of the projects module. Other modules import ONLY this file."""

import uuid

from geolens.modules.projects import service
from geolens.modules.projects.schemas import BrandOut, ProjectSnapshot, PromptOut

__all__ = ["BrandOut", "ProjectNotFoundError", "ProjectSnapshot", "PromptOut", "get_snapshot"]

ProjectNotFoundError = service.ProjectNotFoundError


def get_snapshot(project_id: uuid.UUID) -> ProjectSnapshot:
    """Brands (own + competitors) and prompts of a project, as plain DTOs."""
    return service.snapshot(project_id)
