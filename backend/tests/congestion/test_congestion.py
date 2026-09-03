from datetime import UTC, datetime

from app.congestion.service import (
    CongestionEngine,
    PortCongestionInput,
    PortTimeWindow,
)
from app.maritime.vessels.intelligence import AISObservation


def _input(scenario: str = "normal", **overrides: object) -> PortCongestionInput:
    values: dict[str, object] = {
        "window": PortTimeWindow(
            port_id="INPRD",
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 1, 2, tzinfo=UTC),
        ),
        "vessel_count": 5,
        "historical_throughput_vessels": 10,
        "berth_occupancy": 0.4,
        "queue_vessels": 1,
        "historical_waiting_hours": [10, 12, 14],
        "scenario": scenario,
    }
    values.update(overrides)
    return PortCongestionInput(**values)


def test_deterministic_prediction_has_wait_percentiles_and_impacts() -> None:
    engine = CongestionEngine()
    arrival = AISObservation(
        vessel_id="v-1",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        position={"latitude": 20, "longitude": 85},
    )

    result = engine.predict(_input(ais_arrivals=[arrival]))

    assert result.p50_waiting_hours <= result.p75_waiting_hours <= result.p90_waiting_hours
    assert result.impact.eta_delay_hours == result.expected_waiting_hours
    assert result.key_drivers


def test_scenarios_are_ordered_and_outage_is_severe() -> None:
    engine = CongestionEngine()
    normal = engine.predict(_input("normal"))
    moderate = engine.predict(_input("moderate"))
    severe = engine.predict(_input("severe"))
    outage = engine.predict(_input("outage"))

    assert normal.congestion_score < moderate.congestion_score < severe.congestion_score
    assert severe.expected_waiting_hours < outage.expected_waiting_hours
    assert outage.impact.recommendation == "avoid or re-time port call"


def test_operational_outage_and_weather_raise_hard_signal() -> None:
    result = CongestionEngine().predict(
        _input(
            "normal",
            operational_status="outage",
            weather_factor=1,
            berth_occupancy=1,
            queue_vessels=10,
        )
    )

    assert result.congestion_score == 1
    assert "operational status" in result.key_drivers
    assert "weather conditions" in result.key_drivers


def test_state_projection_does_not_mutate_state_or_inputs() -> None:
    engine = CongestionEngine()
    state_data = {"vessel_id": "v-1", "latitude": 20, "longitude": 85}
    from app.maritime.state_vector import StateComponent, build_state_vector

    state = build_state_vector(
        {"ais": StateComponent(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            source="synthetic",
            quality=1,
            freshness={
                "state": "FRESH",
                "age_seconds": 0,
                "threshold_seconds": 900,
                "evaluated_at": datetime(2026, 1, 1, tzinfo=UTC),
            },
            status="SYNTHETIC",
            data=state_data,
        )},
        decision_session_id="00000000-0000-0000-0000-000000000001",
    )
    before = state.model_dump(mode="json")

    engine.from_state_vector(state, _input().window)

    assert state.model_dump(mode="json") == before