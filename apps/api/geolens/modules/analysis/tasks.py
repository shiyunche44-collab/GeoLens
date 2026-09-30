import uuid

from geolens.core import events
from geolens.core.queue import tenant_task
from geolens.modules.analysis import service
from geolens.modules.collection import public as collection


@tenant_task(service.ANALYZE_TASK, queue="analyze")
def analyze_response(response_id: str, project_id: str) -> None:
    service.analyze_response(uuid.UUID(response_id))


events.subscribe(collection.RESPONSE_COLLECTED, service.ANALYZE_TASK, queue="analyze")
