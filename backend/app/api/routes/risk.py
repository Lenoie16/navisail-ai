"""Monte Carlo risk simulation endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.risk.monte_carlo import (
    SimulationAlternative,
    SimulationOutput,
    monte_carlo_engine,
)
from app.risk.regime import MarketRegimeState, MarketSignal, market_regime_detector
from app.risk.scenarios import RiskScenario

router = APIRouter(prefix="/risk", tags=["risk"])


class SimulationRequest(BaseModel):
    alternatives: tuple[SimulationAlternative, ...]
    scenario: RiskScenario
    simulations: int = Field(default=10_000, gt=0)
    seed: int = 0


@router.post("/simulate", response_model=list[SimulationOutput])
async def simulate_risk(request: SimulationRequest) -> list[SimulationOutput]:
    return monte_carlo_engine.simulate(
        request.alternatives,
        scenario=request.scenario,
        simulations=request.simulations,
        seed=request.seed,
    )


@router.post("/compare", response_model=dict[str, SimulationOutput])
async def compare_risk(
    request: SimulationRequest,
) -> dict[str, SimulationOutput]:
    return monte_carlo_engine.compare(
        request.alternatives,
        scenario=request.scenario,
        simulations=request.simulations,
        seed=request.seed,
    )


class RegimeRequest(BaseModel):
    signals: tuple[MarketSignal, ...]
    source_state_snapshot: str | None = None


@router.post("/regime", response_model=MarketRegimeState)
async def detect_market_regime(request: RegimeRequest) -> MarketRegimeState:
    from uuid import UUID

    return market_regime_detector.detect(
        request.signals,
        source_state_snapshot=UUID(request.source_state_snapshot)
        if request.source_state_snapshot
        else None,
    )
