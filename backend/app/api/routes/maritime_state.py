"""MaritimeStateVector snapshot API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.maritime.state_vector import (
    MaritimeStateVector,
    StateComponent,
    StateDiff,
    build_state_vector,
    diff_state_vectors,
    snapshot_store,
)
from app.maritime.vessels.intelligence import (
    AISObservation,
    ShipmentRequirement,
    VesselCandidate,
    VesselProfile,
    vessel_intelligence,
)
from app.events.publisher import publish_event

router = APIRouter(prefix="/maritime-state", tags=["maritime-state"])


class SnapshotRequest(BaseModel):
    decision_session_id: UUID
    version: int = Field(default=1, ge=1)
    effective_at: datetime | None = None
    generated_at: datetime | None = None
    components: dict[str, StateComponent | dict[str, Any]]


class AISIngestRequest(BaseModel):
    vessel_id: str = Field(min_length=1)
    observed_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_knots: float = Field(default=0, ge=0)
    heading_degrees: float | None = Field(default=None, ge=0, lt=360)
    status: str = "underway"
    source: str = "ais"


@router.post("/snapshots", response_model=MaritimeStateVector, status_code=201)
async def create_snapshot(request: SnapshotRequest) -> MaritimeStateVector:
    snapshot = build_state_vector(
        request.components,
        decision_session_id=request.decision_session_id,
        version=request.version,
        effective_at=request.effective_at,
        generated_at=request.generated_at,
    )
    result = snapshot_store.save(snapshot)
    await publish_event(
        "maritime.state.updated",
        decision_session_id=result.decision_session_id,
        aggregate_id=str(result.snapshot_id),
        payload=result.model_dump(mode="json"),
    )
    return result


@router.get("/snapshots/{snapshot_id}", response_model=MaritimeStateVector)
async def get_snapshot(snapshot_id: UUID) -> MaritimeStateVector:
    snapshot = snapshot_store.get(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="maritime state snapshot not found")
    return snapshot


@router.get("/sessions/{decision_session_id}/snapshots", response_model=list[MaritimeStateVector])
async def get_session_snapshots(decision_session_id: UUID) -> list[MaritimeStateVector]:
    return snapshot_store.by_session(decision_session_id)


@router.get("/snapshots/{before_id}/compare/{after_id}", response_model=StateDiff)
async def compare_snapshots(before_id: UUID, after_id: UUID) -> StateDiff:
    before = snapshot_store.get(before_id)
    after = snapshot_store.get(after_id)
    if before is None or after is None:
        raise HTTPException(status_code=404, detail="maritime state snapshot not found")
    return diff_state_vectors(before, after)


@router.post("/vessels/ais", response_model=AISObservation, status_code=201)
async def ingest_vessel_ais(request: AISIngestRequest) -> AISObservation:
    observation = AISObservation(
        vessel_id=request.vessel_id,
        observed_at=request.observed_at,
        position={"latitude": request.latitude, "longitude": request.longitude},
        speed_knots=request.speed_knots,
        heading_degrees=request.heading_degrees,
        status=request.status,
        source=request.source,
    )
    return vessel_intelligence.ingest(observation)


@router.get("/vessels/{vessel_id}/track", response_model=list[AISObservation])
async def get_vessel_track(vessel_id: str) -> list[AISObservation]:
    return vessel_intelligence.track_history(vessel_id)


class CandidateRequest(BaseModel):
    vessels: list[VesselProfile]
    requirement: ShipmentRequirement


@router.post("/vessels/candidates", response_model=list[VesselCandidate])
async def evaluate_vessel_candidates(request: CandidateRequest) -> list[VesselCandidate]:
    return vessel_intelligence.candidates(request.vessels, request.requirement)
