from datetime import UTC, datetime, timedelta

from app.maritime.vessels.intelligence import (
    GeoPoint,
    ShipmentRequirement,
    VesselIntelligence,
    VesselProfile,
    normalize_ais,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _vessel(vessel_id: str = "v-1", **kwargs: object) -> VesselProfile:
    values: dict[str, object] = {
        "name": "Aurora",
        "vessel_class": "Panamax",
        "capacity_tonnes": 80_000,
    }
    values.update(kwargs)
    return VesselProfile(vessel_id=vessel_id, **values)


def _requirement(**kwargs: object) -> ShipmentRequirement:
    return ShipmentRequirement(
        origin=GeoPoint(latitude=0, longitude=0),
        destination=GeoPoint(latitude=10, longitude=0),
        quantity_tonnes=50_000,
        vessel_classes=frozenset({"Panamax"}),
        ready_at=NOW,
        required_by=NOW + timedelta(days=10),
        **kwargs,
    )


def test_normalize_ingest_track_and_analyze_movement() -> None:
    intelligence = VesselIntelligence()
    intelligence.ingest(
        normalize_ais(
            {
                "vessel_id": "v-1",
                "observed_at": NOW,
                "latitude": 1,
                "longitude": 2,
                "speed_knots": 10,
                "heading_degrees": 90,
            }
        )
    )
    intelligence.ingest(
        normalize_ais(
            {
                "vessel_id": "v-1",
                "observed_at": NOW + timedelta(hours=1),
                "latitude": 1.1,
                "longitude": 2,
                "speed_knots": 14,
                "heading_degrees": 91,
            }
        )
    )

    assert len(intelligence.track_history("v-1")) == 2
    assert intelligence.speed_analysis("v-1")["average_knots"] == 12
    assert intelligence.direction_analysis("v-1")["latest_heading_degrees"] == 91


def test_eta_is_explicit_baseline_estimate() -> None:
    intelligence = VesselIntelligence()
    intelligence.ingest(
        normalize_ais(
            {
                "vessel_id": "v-1",
                "observed_at": NOW,
                "latitude": 0,
                "longitude": 0,
                "speed_knots": 10,
            }
        )
    )

    estimate = intelligence.eta(_vessel(), GeoPoint(latitude=0, longitude=10))

    assert estimate.is_estimate is True
    assert estimate.assumed_speed_knots == 10
    assert estimate.estimated_arrival_at > NOW


def test_candidates_filter_and_explain_unavailable_vessels() -> None:
    intelligence = VesselIntelligence()
    intelligence.ingest(
        normalize_ais(
            {
                "vessel_id": "v-1",
                "observed_at": NOW,
                "latitude": 0,
                "longitude": 0,
                "speed_knots": 12,
            }
        )
    )
    viable = _vessel()
    unavailable = _vessel(
        "v-2", status="maintenance", vessel_class="Tanker", capacity_tonnes=10_000
    )

    candidates = intelligence.candidates([viable, unavailable], _requirement())

    assert candidates[0].vessel.vessel_id == "v-1"
    assert candidates[0].estimated_readiness.destination.latitude == 0
    assert candidates[1].exclusion_reasons == (
        "vessel is not active",
        "vessel class is incompatible",
        "capacity is insufficient",
    )