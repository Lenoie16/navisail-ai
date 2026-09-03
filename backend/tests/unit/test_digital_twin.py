from datetime import UTC, datetime

from app.digital_twin.simulation import DigitalTwinSimulator
from app.digital_twin.state import TwinScenarioParameters
from app.maritime.state_vector import StateComponent, build_state_vector


def _snapshot():
    component = StateComponent(
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
        data={"quantity_tonnes": 1000, "inventory_location": "plant-1"},
    )
    return build_state_vector(
        {"shipment": component, "inventory": component},
        decision_session_id="00000000-0000-0000-0000-000000000001",
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_simulation_is_deterministic_and_returns_transitions() -> None:
    simulator = DigitalTwinSimulator()
    snapshot = _snapshot()
    parameters = TwinScenarioParameters(
        booking_date=datetime(2026, 1, 2, tzinfo=UTC),
        vessel_id="v-1",
        port_id="p-1",
        route_id="r-1",
        delay_hours=3,
    )

    first = simulator.simulate(snapshot, scenario_id="what-if", parameters=parameters)
    second = simulator.simulate(snapshot, scenario_id="what-if", parameters=parameters)

    assert first == second
    assert first.source_snapshot_id == snapshot.snapshot_id
    assert [event.event_type for event in first.timeline] == [
        "vessel departure",
        "vessel delay",
        "port arrival",
        "queue formation",
        "berth assignment",
        "loading/discharge",
        "departure",
        "inland arrival",
        "inventory consumption",
    ]
    assert first.final_state.voyage_states["voyage"] == "inventory_consumed"


def test_what_if_does_not_mutate_production_baseline() -> None:
    simulator = DigitalTwinSimulator()
    snapshot = _snapshot()
    before = snapshot.model_dump(mode="json")

    simulator.simulate(
        snapshot,
        parameters=TwinScenarioParameters(
            port_id="alternate-port",
            contract="COA",
        ),
    )

    assert snapshot.model_dump(mode="json") == before
