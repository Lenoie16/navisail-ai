"""Physical compatibility API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.maritime.compatibility.service import (
    CargoConstraints,
    CompatibilityResult,
    PortCapability,
    VesselTechnicalProfile,
    compatibility_engine,
)

router = APIRouter(prefix="/compatibility", tags=["compatibility"])


class CompatibilityCheckRequest(BaseModel):
    vessel: VesselTechnicalProfile
    port: PortCapability
    cargo: CargoConstraints
    berth_id: str | None = None


@router.post("/check", response_model=CompatibilityResult)
async def compatibility_check(request: CompatibilityCheckRequest) -> CompatibilityResult:
    berth = next((item for item in request.port.berths if item.berth_id == request.berth_id), None)
    return compatibility_engine.check(request.vessel, request.port, request.cargo, berth)


class VesselCandidateCompatibilityRequest(BaseModel):
    vessels: list[VesselTechnicalProfile]
    port: PortCapability
    cargo: CargoConstraints


@router.post("/vessels", response_model=dict[str, CompatibilityResult])
async def vessel_candidate_compatibility(
    request: VesselCandidateCompatibilityRequest,
) -> dict[str, CompatibilityResult]:
    return compatibility_engine.vessel_candidate_compatibility(
        request.vessels, request.port, request.cargo
    )


class PortCandidateMatrixRequest(BaseModel):
    vessel: VesselTechnicalProfile
    ports: list[PortCapability]
    cargo: CargoConstraints


@router.post("/ports", response_model=dict[str, CompatibilityResult])
async def port_candidate_matrix(
    request: PortCandidateMatrixRequest,
) -> dict[str, CompatibilityResult]:
    return compatibility_engine.port_candidate_matrix(request.vessel, request.ports, request.cargo)


class BerthCandidateMatrixRequest(BaseModel):
    vessel: VesselTechnicalProfile
    port: PortCapability
    cargo: CargoConstraints


@router.post("/berths", response_model=dict[str, CompatibilityResult])
async def berth_candidate_matrix(
    request: BerthCandidateMatrixRequest,
) -> dict[str, CompatibilityResult]:
    return compatibility_engine.berth_candidate_matrix(request.vessel, request.port, request.cargo)