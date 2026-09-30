"""Celery app + name-based dispatch.

Services enqueue by task *name* (``enqueue("collection.collect", ...)``) so a
service never imports its own ``tasks`` module (tasks sit above services).
Tasks are registered by importing them in ``geolens.app.bootstrap``.
"""

import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any

from celery import Celery

from geolens.core.config import get_settings
from geolens.core.tenancy import workspace_context

QUEUES = ("default", "collect.cn", "collect.global", "analyze", "audit")

_settings = get_settings()
celery_app = Celery("geolens", broker=_settings.redis_url, backend=_settings.redis_url)
celery_app.conf.update(
    task_default_queue="default",
    task_always_eager=_settings.celery_eager,
    task_eager_propagates=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    accept_content=["json"],
)


def tenant_task(name: str, queue: str = "default", **opts: Any) -> Callable[..., Any]:
    """Register a Celery task that runs inside ``workspace_context(workspace_id)``.

    The wrapped function receives every kwarg except ``workspace_id``.
    """

    def decorator(fn: Callable[..., Any]) -> Any:
        @wraps(fn)
        def run(*, workspace_id: str, **kwargs: Any) -> Any:
            with workspace_context(uuid.UUID(workspace_id)):
                return fn(**kwargs)

        return celery_app.task(name=name, queue=queue, **opts)(run)

    return decorator


def enqueue(
    task_name: str, *, workspace_id: uuid.UUID, queue: str | None = None, **kwargs: Any
) -> None:
    task = celery_app.tasks[task_name]
    options: dict[str, Any] = {"queue": queue} if queue else {}
    task.apply_async(kwargs={"workspace_id": str(workspace_id), **kwargs}, **options)
