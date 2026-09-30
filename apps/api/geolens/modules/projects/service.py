import uuid

from geolens.core.db import session_scope
from geolens.modules.projects.models import Brand, Project, Prompt
from geolens.modules.projects.repository import (
    BrandRepository,
    ProjectRepository,
    PromptRepository,
)
from geolens.modules.projects.schemas import (
    BrandCreate,
    BrandOut,
    ProjectCreate,
    ProjectOut,
    ProjectSnapshot,
    PromptCreate,
    PromptOut,
)


class ProjectNotFoundError(LookupError):
    pass


def create_project(data: ProjectCreate) -> ProjectOut:
    with session_scope() as s:
        project = ProjectRepository(s).add(Project(**data.model_dump()))
        return ProjectOut.model_validate(project)


def list_projects() -> list[ProjectOut]:
    with session_scope() as s:
        return [ProjectOut.model_validate(p) for p in ProjectRepository(s).list()]


def get_project(project_id: uuid.UUID) -> ProjectOut:
    with session_scope() as s:
        project = ProjectRepository(s).get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return ProjectOut.model_validate(project)


def add_brand(project_id: uuid.UUID, data: BrandCreate) -> BrandOut:
    get_project(project_id)
    with session_scope() as s:
        brand = BrandRepository(s).add(Brand(project_id=project_id, **data.model_dump()))
        return BrandOut.model_validate(brand)


def add_prompt(project_id: uuid.UUID, data: PromptCreate) -> PromptOut:
    get_project(project_id)
    with session_scope() as s:
        prompt = PromptRepository(s).add(Prompt(project_id=project_id, **data.model_dump()))
        return PromptOut.model_validate(prompt)


def snapshot(project_id: uuid.UUID) -> ProjectSnapshot:
    p = get_project(project_id)
    return ProjectSnapshot(
        id=p.id, name=p.name, default_locale=p.default_locale, brands=p.brands, prompts=p.prompts
    )
