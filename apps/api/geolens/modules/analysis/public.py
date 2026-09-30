"""Public interface of the analysis module. Other modules import ONLY this file."""

import uuid

from geolens.modules.analysis import service
from geolens.modules.analysis.events import RESPONSE_ANALYZED
from geolens.modules.analysis.schemas import ResponseFacts

__all__ = ["RESPONSE_ANALYZED", "ResponseFacts", "list_response_facts"]


def list_response_facts(project_id: uuid.UUID) -> list[ResponseFacts]:
    """One observation per analyzed response: who was mentioned where, who was cited."""
    return service.list_response_facts(project_id)
