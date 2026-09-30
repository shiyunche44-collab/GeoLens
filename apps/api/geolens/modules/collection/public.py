"""Public interface of the collection module. Other modules import ONLY this file."""

import uuid

from geolens.modules.collection import service
from geolens.modules.collection.events import RESPONSE_COLLECTED, RUN_COMPLETED
from geolens.modules.collection.schemas import ResponseOut

__all__ = ["RESPONSE_COLLECTED", "RUN_COMPLETED", "ResponseOut", "get_response"]


def get_response(response_id: uuid.UUID) -> ResponseOut:
    """A collected answer (text + engine-parsed citations) as a DTO."""
    return service.get_response(response_id)
