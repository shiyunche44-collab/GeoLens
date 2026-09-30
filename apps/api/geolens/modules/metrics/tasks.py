import uuid

from geolens.core import events
from geolens.core.queue import tenant_task
from geolens.modules.analysis import public as analysis
from geolens.modules.metrics import service


@tenant_task(service.RECOMPUTE_TASK, queue="analyze")
def recompute_project(project_id: str, response_id: str | None = None) -> None:
    service.recompute_project(uuid.UUID(project_id))


events.subscribe(analysis.RESPONSE_ANALYZED, service.RECOMPUTE_TASK, queue="analyze")
