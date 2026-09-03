"""Landed cost calculation endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.landed_cost.service import landed_cost_engine
from app.schemas.cost import (
	CostComponentInput,
	FXQuote,
	LandedCostResult,
	ScenarioAdjustment,
)

router = APIRouter(prefix="/landed-cost", tags=["landed-cost"])


class LandedCostRequest(BaseModel):
	components: list[CostComponentInput] = Field(default_factory=list)
	quantity_tonnes: float = Field(gt=0)
	target_currency: str = Field(min_length=3, max_length=3)
	fx_quotes: list[FXQuote] = Field(default_factory=list)
	scenario: ScenarioAdjustment | None = None


@router.post("/calculate", response_model=LandedCostResult)
async def calculate_landed_cost(request: LandedCostRequest) -> LandedCostResult:
	return landed_cost_engine.calculate(
		request.components,
		quantity_tonnes=request.quantity_tonnes,
		target_currency=request.target_currency,
		fx_quotes=request.fx_quotes,
		scenario=request.scenario,
	)
