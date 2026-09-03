"""Digital-twin simulation endpoint."""

from fastapi import APIRouter

from app.digital_twin.simulation import TwinSimulationResult, digital_twin_simulator
from app.digital_twin.state import TwinScenarioParameters
from app.maritime.state_vector import MaritimeStateVector

router = APIRouter(prefix="/digital-twin", tags=["digital-twin"])


class TwinSimulationRequest(MaritimeStateVector):
    pass


@router.post("/simulate", response_model=TwinSimulationResult)
async def simulate_digital_twin(
    request: TwinSimulationRequest,
    scenario_id: str = "baseline",
    parameters: TwinScenarioParameters | None = None,
) -> TwinSimulationResult:
    return digital_twin_simulator.simulate(
        request,
        scenario_id=scenario_id,
        parameters=parameters,
    )
