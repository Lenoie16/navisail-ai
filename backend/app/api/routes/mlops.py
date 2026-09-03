"""Model governance and monitoring API."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import Permission, require_permission
from app.mlops.drift import mean_absolute_error, population_drift
from app.mlops.evaluation import chronological_validation
from app.mlops.feedback import OutcomeFeedback, feedback_service
from app.mlops.monitoring import MonitoringRecord, monitoring_service
from app.mlops.registry import ModelLifecycle, ModelRecord, model_registry

router = APIRouter(prefix="/mlops", tags=["mlops"])


class PromotionRequest(BaseModel):
    target: ModelLifecycle


class EvaluationRequest(BaseModel):
    actuals: list[float] = Field(min_length=2)
    predictions: list[float] = Field(min_length=2)
    benchmark: list[float] | None = None


class DriftRequest(BaseModel):
    reference: list[float] = Field(min_length=1)
    current: list[float] = Field(min_length=1)


@router.get("/models", response_model=tuple[ModelRecord, ...])
async def list_models(principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    return model_registry.list()


@router.post("/models", response_model=ModelRecord, status_code=201)
async def register_model(model: ModelRecord, principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    try:
        return model_registry.register(model)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/models/{model_name}/{version}/promote", response_model=ModelRecord)
async def promote_model(model_name: str, version: str, request: PromotionRequest, principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    try:
        return model_registry.promote(model_name, version, request.target)
    except (KeyError, ValueError, PermissionError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/evaluate")
async def evaluate(request: EvaluationRequest, principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    try:
        return chronological_validation(request.actuals, request.predictions, benchmark=request.benchmark)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/monitoring", response_model=MonitoringRecord, status_code=201)
async def record_monitoring(record: MonitoringRecord, principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    return monitoring_service.record(record)


@router.post("/feedback", response_model=OutcomeFeedback, status_code=201)
async def record_feedback(feedback: OutcomeFeedback, principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    return feedback_service.record(feedback)


@router.post("/drift")
async def calculate_drift(request: DriftRequest, principal=Depends(require_permission(Permission.MANAGE_MODEL))):
    try:
        return {"drift_score": population_drift(request.reference, request.current)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
