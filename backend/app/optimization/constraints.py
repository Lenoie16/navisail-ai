"""Constraint evaluation for optimization candidates."""

from app.optimization.models import ConstraintStatus, OptimizationOption, OptimizationProblem


def evaluate_constraints(
    problem: OptimizationProblem, option: OptimizationOption
) -> tuple[ConstraintStatus, ...]:
    checks = [
        (
            "option feasibility",
            option.feasible,
            True,
            "; ".join(option.hard_failures) or "feasible",
        ),
        (
            "cargo quantity",
            option.capacity_tonnes >= problem.quantity_tonnes,
            True,
            f"capacity {option.capacity_tonnes} tonnes",
        ),
        (
            "risk tolerance",
            option.risk_score <= problem.risk_tolerance,
            True,
            f"risk {option.risk_score}",
        ),
        (
            "booking deadline",
            option.available_at <= problem.booking_deadline,
            True,
            f"available at {option.available_at.isoformat()}",
        ),
    ]
    if option.laycan_end:
        checks.append(
            (
                "laycan",
                option.laycan_end >= problem.booking_deadline,
                False,
                "laycan end checked against deadline",
            )
        )
    checks.append(
        (
            "plant continuity",
            option.continuity_acceptable,
            True,
            f"stockout probability {option.stockout_probability}",
        ),
    )
    return tuple(
        ConstraintStatus(name=name, satisfied=satisfied, hard=hard, detail=detail)
        for name, satisfied, hard, detail in checks
    )


__all__ = ["evaluate_constraints"]
