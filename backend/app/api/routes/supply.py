"""Plant supply risk endpoints."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.supply.service import PlantSupplyPlan, SupplyProjection, supply_risk_engine

router = APIRouter(prefix="/supply", tags=["supply"])


class SupplyProjectionRequest(BaseModel):
    plan: PlantSupplyPlan
    as_of: datetime
    horizon_days: int = Field(default=90, gt=0)
    delay_scenarios: tuple[float, ...] = ()
    stockout_probability_limit: float = Field(default=0.2, ge=0, le=1)


@router.post("/project", response_model=SupplyProjection)
async def project_supply(request: SupplyProjectionRequest) -> SupplyProjection:
    return supply_risk_engine.project(
        request.plan,
        as_of=request.as_of,
        horizon_days=request.horizon_days,
        delay_scenarios=request.delay_scenarios,
        stockout_probability_limit=request.stockout_probability_limit,
    )
