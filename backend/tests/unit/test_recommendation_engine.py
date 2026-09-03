from datetime import UTC, datetime

from app.maritime.state_vector import StateComponent, build_state_vector
from app.optimization.models import OptimizationOption, OptimizationProblem
from app.recommendations.recommendation import DecisionSessionInput
from app.recommendations.service import RecommendationEngine

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _snapshot():
    component = StateComponent(
        timestamp=NOW,
        source="demo",
        quality=1,
        freshness={
            "state": "FRESH",
            "age_seconds": 0,
            "threshold_seconds": 900,
            "evaluated_at": NOW,
        },
        status="DEMO",
        data={"port_id": "p-1"},
    )
    return build_state_vector(
        {"port": component},
        decision_session_id="00000000-0000-0000-0000-000000000001",
        effective_at=NOW,
        generated_at=NOW,
    )


def _problem() -> OptimizationProblem:
    base = {
        "vessel_id": "v-1",
        "port_id": "p-1",
        "berth_id": "b-1",
        "route_id": "r-1",
        "available_at": NOW,
        "capacity_tonnes": 2_000,
    }
    return OptimizationProblem(
        shipment_id="ship-1",
        quantity_tonnes=1_000,
        booking_deadline=NOW,
        inventory_available_tonnes=1_000,
        options=(
            OptimizationOption(option_id="cheap", cost_per_tonne=5, **base),
            OptimizationOption(
                option_id="reliable",
                cost_per_tonne=10,
                schedule_reliability=0.99,
                **{**base, "vessel_id": "v-2", "port_id": "p-2"},
            ),
        ),
    )


def test_recommendation_is_deterministic_and_ranks_numerical_outputs() -> None:
    session = DecisionSessionInput(
        session_id="session-1",
        maritime_state=_snapshot(),
        optimization_problem=_problem(),
        preferred_strategy="COA",
        preferred_contract="COA-2026",
        forecast={"model_version": "freight-v1"},
        inventory={"stockout_probability": 0.05},
        risk={"port_outage": "severe"},
        model_versions={"optimizer": "enumeration-v1"},
    )
    engine = RecommendationEngine()

    first = engine.recommend(session)
    second = engine.recommend(session)

    assert first == second
    assert first.decision == "Recommended"
    assert first.preferred_vessel == "v-1"
    assert first.expected_landed_cost == 5_000
    assert first.risk_adjusted_cost == 5_000
    assert first.source_state_snapshot == str(session.maritime_state.snapshot_id)
    assert first.reproducibility_key
    assert len(first.alternatives) == 1


def test_no_feasible_alternative_is_explicit() -> None:
    problem = _problem().model_copy(
        update={
            "options": (
                _problem().options[0].model_copy(update={"continuity_acceptable": False}),
            )
        }
    )
    session = DecisionSessionInput(
        session_id="session-2", maritime_state=_snapshot(), optimization_problem=problem
    )

    result = RecommendationEngine().recommend(session)

    assert result.decision == "No Feasible Alternative"
    assert result.preferred_vessel is None
    assert result.major_downside_scenarios == ("cheap: plant continuity",)