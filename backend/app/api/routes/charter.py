"""Charter timing decision endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.charter.service import (
    BookingCandidate,
    CharterDecision,
    CurrentBooking,
    timing_engine,
)

router = APIRouter(prefix="/charter", tags=["charter"])


class CharterTimingRequest(BaseModel):
    current: CurrentBooking
    candidates: list[BookingCandidate] = Field(default_factory=list)
    risk_cost_per_unit: float = Field(default=1, ge=0)
    neutral_threshold: float = Field(default=0.02, ge=0)


@router.post("/timing", response_model=CharterDecision)
async def evaluate_charter_timing(request: CharterTimingRequest) -> CharterDecision:
    return timing_engine.evaluate(
        request.current,
        request.candidates,
        risk_cost_per_unit=request.risk_cost_per_unit,
        neutral_threshold=request.neutral_threshold,
    )