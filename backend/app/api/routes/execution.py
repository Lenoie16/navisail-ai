"""Approval and execution workflow endpoints."""

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.audit.service import audit_service
from app.audit.trail import record_transition
from app.execution.approvals import ApprovalDecision, ApprovalStatus, approval_service
from app.execution.workflow import (
    ExecutionRecord,
    ExecutionStatus,
    execution_service,
)
from app.events.publisher import publish_event
from app.core.security import Permission, require_permission

router = APIRouter(prefix="/execution", tags=["execution"])


class ApprovalCreateRequest(BaseModel):
    recommendation_id: str = Field(min_length=1)
    recommendation_version: str = Field(min_length=1)
    user: str = Field(min_length=1)
    role: str = Field(min_length=1)
    expires_hours: float | None = Field(default=None, gt=0)


class ApprovalDecisionRequest(BaseModel):
    user: str = Field(min_length=1)
    role: str = Field(min_length=1)
    status: ApprovalStatus
    comment: str = ""


class ExecutionCreateRequest(BaseModel):
    recommendation_id: str = Field(min_length=1)
    user: str = Field(min_length=1)


class ExecutionTransitionRequest(BaseModel):
    target: ExecutionStatus
    user: str = Field(min_length=1)
    approval_id: UUID | None = None
    approval_status: ApprovalStatus | None = None


@router.post("/approvals", response_model=ApprovalDecision)
async def create_approval(request: ApprovalCreateRequest, principal=Depends(require_permission(Permission.APPROVE_RECOMMENDATION))) -> ApprovalDecision:
    if (request.user, request.role) != principal:
        raise HTTPException(status_code=403, detail="request identity does not match authenticated principal")
    try:
        result = approval_service.create(
            request.recommendation_id,
            request.recommendation_version,
            request.user,
            request.role,
            expires_in=timedelta(hours=request.expires_hours)
            if request.expires_hours
            else None,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    record_transition(
        actor=request.user,
        entity_type="approval",
        entity_id=str(result.decision_id),
        action="created",
        details=result.model_dump(mode="json"),
    )
    await publish_event(
        "approval.changed",
        aggregate_id=str(result.decision_id),
        payload=result.model_dump(mode="json"),
    )
    return result


@router.post("/approvals/{decision_id}/decide", response_model=ApprovalDecision)
async def decide_approval(
    decision_id: UUID, request: ApprovalDecisionRequest,
    principal=Depends(require_permission(Permission.APPROVE_RECOMMENDATION)),
) -> ApprovalDecision:
    if (request.user, request.role) != principal:
        raise HTTPException(status_code=403, detail="request identity does not match authenticated principal")
    try:
        result = approval_service.decide(
            decision_id,
            user=request.user,
            role=request.role,
            status=request.status,
            comment=request.comment,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    record_transition(
        actor=request.user,
        entity_type="approval",
        entity_id=str(decision_id),
        action="decided",
        details=result.model_dump(mode="json"),
    )
    await publish_event(
        "approval.changed",
        aggregate_id=str(decision_id),
        payload=result.model_dump(mode="json"),
    )
    return result


@router.post("/executions", response_model=ExecutionRecord)
async def create_execution(request: ExecutionCreateRequest, principal=Depends(require_permission(Permission.EXECUTE_BOOKING))) -> ExecutionRecord:
    if request.user != principal[0]:
        raise HTTPException(status_code=403, detail="request identity does not match authenticated principal")
    result = execution_service.create(request.recommendation_id, request.user)
    await publish_event(
        "execution.changed",
        aggregate_id=str(result.execution_id),
        payload=result.model_dump(mode="json"),
    )
    return result


@router.post("/executions/{execution_id}/transition", response_model=ExecutionRecord)
async def transition_execution(
    execution_id: UUID, request: ExecutionTransitionRequest,
    principal=Depends(require_permission(Permission.EXECUTE_BOOKING)),
) -> ExecutionRecord:
    if request.user != principal[0]:
        raise HTTPException(status_code=403, detail="request identity does not match authenticated principal")
    try:
        result = execution_service.transition(
            execution_id,
            request.target,
            user=request.user,
            approval_status=request.approval_status,
            approval_id=request.approval_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    record_transition(
        actor=request.user,
        entity_type="execution",
        entity_id=str(execution_id),
        action="transition",
        details=result.model_dump(mode="json"),
    )
    await publish_event(
        "execution.changed",
        aggregate_id=str(execution_id),
        payload=result.model_dump(mode="json"),
    )
    return result


@router.get("/audit/{entity_type}/{entity_id}")
async def get_audit(entity_type: str, entity_id: str):
    return audit_service.for_entity(entity_type, entity_id)
