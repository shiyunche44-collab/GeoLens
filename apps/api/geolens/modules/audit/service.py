import logging
import uuid

from geolens.core.db import session_scope, utcnow
from geolens.core.queue import enqueue
from geolens.core.tenancy import current_workspace_id
from geolens.modules.audit import crawler, rules
from geolens.modules.audit.models import AuditFinding, AuditJob
from geolens.modules.audit.repository import AuditJobRepository
from geolens.modules.audit.schemas import AuditCreate, AuditOut
from geolens.modules.identity import public as identity

log = logging.getLogger(__name__)

AUDIT_TASK = "audit.run"


class AuditNotFoundError(LookupError):
    pass


def create_audit(data: AuditCreate) -> AuditOut:
    url = str(data.url)
    crawler.assert_public_http_url(url)
    with session_scope() as s:
        job = AuditJobRepository(s).add(AuditJob(url=url, project_id=data.project_id))
        job_id = job.id
    enqueue(AUDIT_TASK, workspace_id=current_workspace_id(), queue="audit", job_id=str(job_id))
    return get_audit(job_id)


def run_audit(job_id: uuid.UUID) -> None:
    with session_scope() as s:
        job = AuditJobRepository(s).get(job_id)
        if job is None or job.status == "done":
            return
        url = job.url
    try:
        ctx = crawler.fetch_site(url)
        findings = rules.run_all(ctx)
    except Exception as e:
        log.exception("audit failed job=%s", job_id)
        with session_scope() as s:
            job = AuditJobRepository(s).get(job_id)
            assert job is not None
            job.status, job.error, job.finished_at = "failed", repr(e)[:2000], utcnow()
        return
    identity.record_usage("audit_crawl", units=1, meta={"url": url})
    ws = current_workspace_id()
    with session_scope() as s:
        job = AuditJobRepository(s).get(job_id)
        assert job is not None
        job.findings = [
            AuditFinding(
                workspace_id=ws,
                rule_id=f.rule_id,
                category=f.category,
                severity=f.severity,
                message=f.message,
                recommendation=f.recommendation,
            )
            for f in findings
        ]
        job.score, job.status, job.finished_at = rules.score(findings), "done", utcnow()


def get_audit(job_id: uuid.UUID) -> AuditOut:
    with session_scope() as s:
        job = AuditJobRepository(s).get(job_id)
        if job is None:
            raise AuditNotFoundError(job_id)
        return AuditOut.model_validate(job)


def list_audits() -> list[AuditOut]:
    with session_scope() as s:
        return [AuditOut.model_validate(j) for j in AuditJobRepository(s).recent()]
