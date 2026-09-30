from geolens.core.repository import WorkspaceRepository
from geolens.modules.projects.models import Brand, Project, Prompt


class ProjectRepository(WorkspaceRepository[Project]):
    model = Project


class BrandRepository(WorkspaceRepository[Brand]):
    model = Brand


class PromptRepository(WorkspaceRepository[Prompt]):
    model = Prompt
