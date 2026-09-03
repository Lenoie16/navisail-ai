from datetime import UTC, datetime

from app.explainability.models import ExplainabilityRequest
from app.explainability.service import ExplainabilityService
from app.maritime.state_vector import StateComponent, build_state_vector
from app.optimization.models import OptimizationOption, OptimizationProblem
from app.recommendations.recommendation import DecisionSessionInput
from app.recommendations.service import RecommendationEngine

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _recommendation():
    component = StateComponent(
        timestamp=NOW,
        source="demo",
        quality=0.8,
        freshness={
            "state": "FRESH",
            "age_seconds": 0,
            "threshold_seconds": 900,
            "evaluated_at": NOW,
        },
        status="DEMO",
        data={"port_id": "p-1"},
    )
    snapshot = build_state_vector(
        {"port": component},
        decision_session_id="00000000-0000-0000-0000-000000000001",
        effective_at=NOW,
        generated_at=NOW,
    )
    base = {
        "vessel_id": "v-1",
        "port_id": "p-1",
        "berth_id": "b-1",
        "route_id": "r-1",
        "available_at": NOW,
        "capacity_tonnes": 2_000,
    }
    problem = OptimizationProblem(
        shipment_id="ship-1",
        quantity_tonnes=1_000,
        booking_deadline=NOW,
        inventory_available_tonnes=1_000,
        options=(
            OptimizationOption(option_id="cheap", cost_per_tonne=5, **base),
            OptimizationOption(
                option_id="safe",
                cost_per_tonne=8,
                schedule_reliability=0.9,
                **{**base, "vessel_id": "v-2"},
            ),
        ),
    )
    return RecommendationEngine().recommend(
        DecisionSessionInput(
            session_id="session-1",
            maritime_state=snapshot,
            optimization_problem=problem,
            model_versions={"optimizer": "enumeration-v1"},
        )
    )


def test_memo_numbers_are_engine_derived() -> None:
    recommendation = _recommendation()
    memo = ExplainabilityService().explain(
        ExplainabilityRequest(recommendation=recommendation)
    )

    assert memo.key_numbers["risk_adjusted_cost"] == recommendation.risk_adjusted_cost
    assert memo.data_confidence == 0.8
    assert memo.alternatives[0].additional_risk_adjusted_cost == 3_100
    assert "v-1" in memo.recommended_action


def test_memo_preserves_reproducibility_metadata() -> None:
    recommendation = _recommendation()
    memo = ExplainabilityService().explain(
        ExplainabilityRequest(recommendation=recommendation)
    )

    assert memo.source_state_snapshot == recommendation.source_state_snapshot
    assert memo.model_versions == recommendation.model_versions
    assert memo.reproducibility_key == recommendation.reproducibility_key
