import uuid

from geolens.core.queue import tenant_task
from geolens.modules.audit import service


@tenant_task(service.AUDIT_TASK, queue="audit")
def run(job_id: str) -> None:
    service.run_audit(uuid.UUID(job_id))
