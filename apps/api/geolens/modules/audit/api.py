import uuid

from fastapi import APIRouter, HTTPException

from geolens.modules.audit import crawler, service
from geolens.modules.audit.schemas import AuditCreate, AuditOut

router = APIRouter(prefix="/audits", tags=["audit"])


@router.post("", response_model=AuditOut, status_code=202)
def create_audit(body: AuditCreate) -> AuditOut:
    try:
        return service.create_audit(body)
    except crawler.UnsafeTargetError as e:
        raise HTTPException(422, str(e)) from e


@router.get("", response_model=list[AuditOut])
def list_audits() -> list[AuditOut]:
    return service.list_audits()


@router.get("/{job_id}", response_model=AuditOut)
def get_audit(job_id: uuid.UUID) -> AuditOut:
    try:
        return service.get_audit(job_id)
    except service.AuditNotFoundError as e:
        raise HTTPException(404, "audit not found") from e
