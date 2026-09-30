"""In-process domain event bus delivered through Celery tasks.

Publishers only know the event name; subscribers register a task name for it
(in their own ``tasks`` module). This keeps modules decoupled and lets P2 swap
the transport (Redis Streams / Kafka / NATS) behind the same API.
"""

import uuid
from collections import defaultdict
from typing import Any

from geolens.core.queue import enqueue

_subscribers: dict[str, list[tuple[str, str | None]]] = defaultdict(list)


def subscribe(event: str, task_name: str, queue: str | None = None) -> None:
    if (task_name, queue) not in _subscribers[event]:
        _subscribers[event].append((task_name, queue))


def publish(event: str, *, workspace_id: uuid.UUID, **payload: Any) -> None:
    for task_name, queue in _subscribers.get(event, []):
        enqueue(task_name, workspace_id=workspace_id, queue=queue, **payload)


def subscribers(event: str) -> list[str]:
    return [name for name, _ in _subscribers.get(event, [])]
