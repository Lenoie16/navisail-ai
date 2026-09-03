"""Unified numerical recommendation endpoint."""

from fastapi import APIRouter

from app.recommendations.recommendation import DecisionSessionInput, Recommendation
from app.recommendations.service import recommendation_engine

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/generate", response_model=Recommendation)
async def generate_recommendation(request: DecisionSessionInput) -> Recommendation:
    return recommendation_engine.recommend(request)
