"""Public interface of the metrics module (P2: alerts, reports and exports consume this)."""

import uuid

from geolens.modules.metrics import service
from geolens.modules.metrics.schemas import ProjectMetricsOut

__all__ = ["ProjectMetricsOut", "get_project_metrics"]


def get_project_metrics(project_id: uuid.UUID) -> ProjectMetricsOut:
    return service.get_project_metrics(project_id)
