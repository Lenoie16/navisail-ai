"""Constrained optimization endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.optimization.models import OptimizationProblem, OptimizationResult
from app.optimization.service import optimization_service
from app.optimization.strategy import (
	MarketCondition,
	StrategyConstraints,
	StrategyOptimizationResult,
	VoyageDemand,
	strategy_optimizer,
)

router = APIRouter(prefix="/optimization", tags=["optimization"])


@router.post("/solve", response_model=OptimizationResult)
async def solve_optimization(request: OptimizationProblem) -> OptimizationResult:
	return optimization_service.optimize(request)


class StrategyRequest(BaseModel):
	voyages: tuple[VoyageDemand, ...]
	market_condition: MarketCondition = "stable"
	constraints: StrategyConstraints | None = None


@router.post("/strategy", response_model=StrategyOptimizationResult)
async def optimize_strategy(request: StrategyRequest) -> StrategyOptimizationResult:
	return strategy_optimizer.optimize(
		request.voyages,
		market_condition=request.market_condition,
		constraints=request.constraints,
	)
