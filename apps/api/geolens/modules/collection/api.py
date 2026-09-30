import uuid

from fastapi import APIRouter, HTTPException

from geolens.modules.collection import service
from geolens.modules.collection.schemas import EngineOut, ResponseOut, RunCreate, RunOut
from geolens.modules.projects import public as projects

router = APIRouter(tags=["collection"])


@router.get("/engines", response_model=list[EngineOut])
def list_engines() -> list[EngineOut]:
    return service.list_engines()


@router.post("/projects/{project_id}/runs", response_model=RunOut, status_code=202)
def create_run(project_id: uuid.UUID, body: RunCreate) -> RunOut:
    try:
        return service.plan_run(project_id, body)
    except projects.ProjectNotFoundError as e:
        raise HTTPException(404, "project not found") from e
    except service.UnknownEngineError as e:
        raise HTTPException(422, str(e)) from e


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: uuid.UUID) -> RunOut:
    try:
        return service.get_run(run_id)
    except service.RunNotFoundError as e:
        raise HTTPException(404, "run not found") from e


@router.get("/runs/{run_id}/responses", response_model=list[ResponseOut])
def list_responses(run_id: uuid.UUID) -> list[ResponseOut]:
    try:
        return service.list_run_responses(run_id)
    except service.RunNotFoundError as e:
        raise HTTPException(404, "run not found") from e
