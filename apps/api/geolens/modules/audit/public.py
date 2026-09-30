"""Public interface of the audit module (P2: reports and alerts consume this)."""

import uuid

from geolens.modules.audit import service
from geolens.modules.audit.schemas import AuditOut

__all__ = ["AuditOut", "get_audit"]


def get_audit(job_id: uuid.UUID) -> AuditOut:
    return service.get_audit(job_id)
