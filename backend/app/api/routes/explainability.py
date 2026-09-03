"""Decision memo endpoint."""

from fastapi import APIRouter

from app.explainability.models import DecisionMemo, ExplainabilityRequest
from app.explainability.service import explainability_service

router = APIRouter(prefix="/explainability", tags=["explainability"])


@router.post("/memo", response_model=DecisionMemo)
async def create_decision_memo(request: ExplainabilityRequest) -> DecisionMemo:
    return explainability_service.explain(request)
