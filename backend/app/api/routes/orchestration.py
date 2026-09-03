"""Asynchronous end-to-end decision workflow endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.security import Permission, require_permission
from app.jobs.tasks import OrchestrationJob, orchestration_service

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


class OrchestrationRequest(BaseModel):
    decision_session_id: str = Field(min_length=1)
    stage_results: dict[str, dict[str, object] | None] = Field(default_factory=dict)
    correlation_id: UUID | None = None


@router.post("/jobs", response_model=OrchestrationJob, status_code=202)
async def start_job(
    request: OrchestrationRequest,
    idempotency_key: str = Header(min_length=1, alias="Idempotency-Key"),
    principal=Depends(require_permission(Permission.RUN_SIMULATION)),
) -> OrchestrationJob:
    return orchestration_service.create(
        decision_session_id=request.decision_session_id,
        idempotency_key=idempotency_key,
        correlation_id=request.correlation_id,
        stages=request.stage_results,
    )


@router.get("/jobs/{job_id}", response_model=OrchestrationJob)
async def get_job(job_id: UUID, principal=Depends(require_permission(Permission.VIEW_DECISIONS))) -> OrchestrationJob:
    try:
        return orchestration_service.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
