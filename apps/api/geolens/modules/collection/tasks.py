"""Celery entrypoints. Thin: unpack args, call the service."""

import uuid

from geolens.core.queue import tenant_task
from geolens.modules.collection import service


@tenant_task(service.COLLECT_TASK)
def collect(task_id: str) -> None:
    service.collect(uuid.UUID(task_id))
