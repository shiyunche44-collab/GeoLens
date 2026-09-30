import uuid

from fastapi import APIRouter, HTTPException

from geolens.modules.metrics import service
from geolens.modules.metrics.schemas import ProjectMetricsOut
from geolens.modules.projects import public as projects

router = APIRouter(tags=["metrics"])


@router.get("/projects/{project_id}/metrics", response_model=ProjectMetricsOut)
def get_metrics(project_id: uuid.UUID) -> ProjectMetricsOut:
    try:
        return service.get_project_metrics(project_id)
    except projects.ProjectNotFoundError as e:
        raise HTTPException(404, "project not found") from e
