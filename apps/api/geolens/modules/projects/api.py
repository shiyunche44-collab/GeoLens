import uuid

from fastapi import APIRouter, HTTPException

from geolens.modules.projects import service
from geolens.modules.projects.schemas import (
    BrandCreate,
    BrandOut,
    ProjectCreate,
    ProjectOut,
    PromptCreate,
    PromptOut,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate) -> ProjectOut:
    return service.create_project(body)


@router.get("", response_model=list[ProjectOut])
def list_projects() -> list[ProjectOut]:
    return service.list_projects()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: uuid.UUID) -> ProjectOut:
    try:
        return service.get_project(project_id)
    except service.ProjectNotFoundError as e:
        raise HTTPException(404, "project not found") from e


@router.post("/{project_id}/brands", response_model=BrandOut, status_code=201)
def add_brand(project_id: uuid.UUID, body: BrandCreate) -> BrandOut:
    try:
        return service.add_brand(project_id, body)
    except service.ProjectNotFoundError as e:
        raise HTTPException(404, "project not found") from e


@router.post("/{project_id}/prompts", response_model=PromptOut, status_code=201)
def add_prompt(project_id: uuid.UUID, body: PromptCreate) -> PromptOut:
    try:
        return service.add_prompt(project_id, body)
    except service.ProjectNotFoundError as e:
        raise HTTPException(404, "project not found") from e
