from datetime import UTC, datetime, timedelta

from app.optimization.models import OptimizationOption, OptimizationProblem
from app.optimization.service import OptimizationService

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _option(option_id: str, **overrides: object) -> OptimizationOption:
    values: dict[str, object] = {
        "option_id": option_id,
        "vessel_id": f"v-{option_id}",
        "port_id": f"p-{option_id}",
        "berth_id": f"b-{option_id}",
        "route_id": f"r-{option_id}",
        "available_at": NOW,
        "capacity_tonnes": 100_000,
        "cost_per_tonne": 20,
    }
    values.update(overrides)
    return OptimizationOption(**values)


def _problem(options: tuple[OptimizationOption, ...], **overrides: object) -> OptimizationProblem:
    values: dict[str, object] = {
        "shipment_id": "ship-1",
        "quantity_tonnes": 50_000,
        "booking_deadline": NOW + timedelta(days=2),
        "inventory_available_tonnes": 60_000,
        "options": options,
    }
    values.update(overrides)
    return OptimizationProblem(**values)


def test_feasible_solution_exposes_variables_constraints_and_penalties() -> None:
    result = OptimizationService().optimize(_problem((_option("a"),)))

    assert result.feasible is True
    assert result.solver_status == "OPTIMAL_ENUMERATION"
    assert result.solution is not None
    assert result.solution.allocated_tonnes == 50_000
    assert result.decision_variables["selected_option"] == "a"
    assert result.solution.constraint_status[0].hard is True


def test_infeasible_problem_excludes_hard_failures() -> None:
    result = OptimizationService().optimize(
        _problem((_option("small", capacity_tonnes=49_999),))
    )

    assert result.feasible is False
    assert result.solver_status == "INFEASIBLE"
    assert result.solution is None
    assert any("cargo quantity" in item for item in result.hard_constraints)


def test_boundary_capacity_and_risk_tolerance_are_respected() -> None:
    result = OptimizationService().optimize(
        _problem((_option("boundary", risk_score=0.5),), risk_tolerance=0.5)
    )

    assert result.feasible is True
    assert result.solution is not None
    assert result.solution.allocated_tonnes == 50_000


def test_conflicting_risk_and_deadline_constraints_are_infeasible() -> None:
    result = OptimizationService().optimize(
        _problem(
            (
                _option(
                    "conflict",
                    risk_score=0.9,
                    available_at=NOW + timedelta(days=3),
                ),
            ),
            risk_tolerance=0.2,
        )
    )

    assert result.feasible is False
    assert len(result.hard_constraints) >= 2


def test_alternative_optimal_solutions_are_returned_deterministically() -> None:
    result = OptimizationService().optimize(
        _problem((_option("b"), _option("a"), _option("c")))
    )

    assert result.solution is not None
    assert result.solution.option_id == "a"
    assert [item.option_id for item in result.alternatives] == ["b", "c"]