"""AIS normalization and deterministic vessel intelligence primitives."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime, timedelta
from typing import Any

from app.maritime.state_vector import MaritimeStateVector
from pydantic import BaseModel, ConfigDict, Field, model_validator


class GeoPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AISObservation(BaseModel):
    """Normalized AIS position used by the intelligence layer."""

    model_config = ConfigDict(extra="forbid")

    vessel_id: str = Field(min_length=1)
    observed_at: datetime
    position: GeoPoint
    speed_knots: float = Field(default=0, ge=0)
    heading_degrees: float | None = Field(default=None, ge=0, lt=360)
    status: str = "underway"
    source: str = "ais"

    @model_validator(mode="after")
    def normalize_time(self) -> AISObservation:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must include a timezone")
        self.observed_at = self.observed_at.astimezone(UTC)
        return self


class VesselProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vessel_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    vessel_class: str = Field(min_length=1)
    capacity_tonnes: float = Field(gt=0)
    status: str = "active"
    expected_completion_at: datetime | None = None
    technical_constraints: tuple[str, ...] = ()
    cruising_speed_knots: float = Field(default=12, gt=0)


class ShipmentRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin: GeoPoint
    destination: GeoPoint
    quantity_tonnes: float = Field(gt=0)
    vessel_classes: frozenset[str] = frozenset()
    ready_at: datetime
    required_by: datetime
    route_distance_nm: float | None = Field(default=None, gt=0)
    max_repositioning_nm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def valid_window(self) -> ShipmentRequirement:
        if self.required_by < self.ready_at:
            raise ValueError("required_by must not precede ready_at")
        return self


class ETAEstimate(BaseModel):
    vessel_id: str
    destination: GeoPoint
    distance_nm: float = Field(ge=0)
    assumed_speed_knots: float = Field(gt=0)
    estimated_arrival_at: datetime
    is_estimate: bool = True
    basis: str = "great-circle distance and assumed speed"


class VesselCandidate(BaseModel):
    vessel: VesselProfile
    estimated_availability: datetime
    capacity_tonnes: float
    technical_constraints: tuple[str, ...]
    estimated_readiness: ETAEstimate
    confidence: float = Field(ge=0, le=1)
    data_freshness: datetime | None
    repositioning_distance_nm: float
    exclusion_reasons: tuple[str, ...] = ()


def great_circle_distance_nm(first: GeoPoint, second: GeoPoint) -> float:
    """Return the shortest surface distance in nautical miles."""

    radius_nm = 3440.065
    lat1, lat2 = math.radians(first.latitude), math.radians(second.latitude)
    delta_lat = lat2 - lat1
    delta_lon = math.radians(second.longitude - first.longitude)
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * radius_nm * math.asin(math.sqrt(haversine))


def normalize_ais(payload: Mapping[str, Any], *, source: str = "ais") -> AISObservation:
    """Normalize common flat AIS fields into the canonical observation shape."""

    position = payload.get("position") or {
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
    }
    return AISObservation(
        vessel_id=str(payload["vessel_id"]),
        observed_at=payload["observed_at"],
        position=position,
        speed_knots=payload.get("speed_knots", 0),
        heading_degrees=payload.get("heading_degrees"),
        status=payload.get("status", "underway"),
        source=source,
    )


class VesselIntelligence:
    """Build vessel movement intelligence from normalized AIS observations."""

    def __init__(self) -> None:
        self._tracks: dict[str, list[AISObservation]] = defaultdict(list)

    def ingest(self, observation: AISObservation | Mapping[str, Any]) -> AISObservation:
        normalized = (
            observation if isinstance(observation, AISObservation) else normalize_ais(observation)
        )
        track = self._tracks[normalized.vessel_id]
        track.append(normalized)
        track.sort(key=lambda item: item.observed_at)
        return normalized

    def track_history(self, vessel_id: str) -> list[AISObservation]:
        return list(self._tracks.get(vessel_id, ()))

    def speed_analysis(self, vessel_id: str) -> dict[str, float | None]:
        speeds = [item.speed_knots for item in self.track_history(vessel_id)]
        return {
            "average_knots": sum(speeds) / len(speeds) if speeds else None,
            "minimum_knots": min(speeds) if speeds else None,
            "maximum_knots": max(speeds) if speeds else None,
            "latest_knots": speeds[-1] if speeds else None,
        }

    def direction_analysis(self, vessel_id: str) -> dict[str, float | None]:
        track = self.track_history(vessel_id)
        headings = [item.heading_degrees for item in track if item.heading_degrees is not None]
        return {
            "latest_heading_degrees": headings[-1] if headings else None,
            "sample_count": len(headings),
        }

    def eta(
        self,
        vessel: VesselProfile,
        destination: GeoPoint,
        *,
        observed_at: datetime | None = None,
        route_distance_nm: float | None = None,
    ) -> ETAEstimate:
        track = self.track_history(vessel.vessel_id)
        latest = track[-1] if track else None
        start = latest.position if latest else destination
        speed = (
            latest.speed_knots
            if latest and latest.speed_knots > 0
            else vessel.cruising_speed_knots
        )
        distance = route_distance_nm or great_circle_distance_nm(start, destination)
        at = (observed_at or (latest.observed_at if latest else datetime.now(UTC))).astimezone(UTC)
        return ETAEstimate(
            vessel_id=vessel.vessel_id,
            destination=destination,
            distance_nm=distance,
            assumed_speed_knots=speed,
            estimated_arrival_at=at + timedelta(hours=distance / speed),
        )

    def candidates(
        self, vessels: Iterable[VesselProfile], requirement: ShipmentRequirement
    ) -> list[VesselCandidate]:
        result: list[VesselCandidate] = []
        for vessel in vessels:
            track = self.track_history(vessel.vessel_id)
            latest = track[-1] if track else None
            repositioning = (
                great_circle_distance_nm(latest.position, requirement.origin)
                if latest
                else math.inf
            )
            readiness = max(
                requirement.ready_at,
                vessel.expected_completion_at or requirement.ready_at,
            )
            eta = self.eta(vessel, requirement.origin, observed_at=readiness)
            reasons = [
                reason
                for condition, reason in (
                    (vessel.status.lower() != "active", "vessel is not active"),
                    (
                        bool(requirement.vessel_classes)
                        and vessel.vessel_class not in requirement.vessel_classes,
                        "vessel class is incompatible",
                    ),
                    (
                        vessel.capacity_tonnes < requirement.quantity_tonnes,
                        "capacity is insufficient",
                    ),
                    (
                        repositioning > (requirement.max_repositioning_nm or math.inf),
                        "repositioning distance exceeds limit",
                    ),
                    (
                        eta.estimated_arrival_at > requirement.required_by,
                        "estimated readiness exceeds required timing",
                    ),
                )
                if condition
            ]
            freshness = latest.observed_at if latest else None
            confidence = 0.9 if latest else 0.45
            if latest and latest.status.lower() not in {"underway", "moored", "at_anchor"}:
                confidence -= 0.2
            result.append(
                VesselCandidate(
                    vessel=vessel,
                    estimated_availability=readiness,
                    capacity_tonnes=vessel.capacity_tonnes,
                    technical_constraints=vessel.technical_constraints,
                    estimated_readiness=eta,
                    confidence=max(0, confidence),
                    data_freshness=freshness,
                    repositioning_distance_nm=repositioning,
                    exclusion_reasons=tuple(reasons),
                )
            )
        return sorted(
            result,
            key=lambda candidate: (
                bool(candidate.exclusion_reasons),
                candidate.estimated_availability,
                -candidate.confidence,
            ),
        )

    @staticmethod
    def from_state_vector(state: MaritimeStateVector) -> list[AISObservation]:
        """Extract AIS observations from a state-vector component without inventing data."""

        component = state.components.get("ais")
        if component is None:
            return []
        values = component.data if isinstance(component.data, list) else [component.data]
        return [normalize_ais(value, source=component.source) for value in values]


vessel_intelligence = VesselIntelligence()

__all__ = [
    "AISObservation",
    "ETAEstimate",
    "GeoPoint",
    "ShipmentRequirement",
    "VesselCandidate",
    "VesselIntelligence",
    "VesselProfile",
    "great_circle_distance_nm",
    "normalize_ais",
    "vessel_intelligence",
]