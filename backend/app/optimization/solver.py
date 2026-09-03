"""Explainable bounded optimization solver."""

from __future__ import annotations

from app.optimization.constraints import evaluate_constraints
from app.optimization.models import (
	OptimizationProblem,
	OptimizationResult,
	OptimizationSolution,
)


class OptimizationSolver:
	"""Solve bounded candidate sets exactly and expose the decision mechanics."""

	solver_status = "OPTIMAL_ENUMERATION"

	def solve(self, problem: OptimizationProblem, *, alternatives: int = 3) -> OptimizationResult:
		ranked: list[OptimizationSolution] = []
		rejected: list[str] = []
		for option in problem.options:
			statuses = evaluate_constraints(problem, option)
			failures = tuple(
				status.name for status in statuses if status.hard and not status.satisfied
			)
			if failures:
				rejected.extend(f"{option.option_id}: {failure}" for failure in failures)
				continue
			penalties = {
				"congestion": option.congestion_penalty,
				"schedule_reliability": 1 - option.schedule_reliability,
				"soft_constraints": float(len(option.soft_constraints)),
			}
			cost = option.cost_per_tonne * problem.quantity_tonnes
			objective = cost + sum(penalties.values()) * problem.quantity_tonnes
			ranked.append(
				OptimizationSolution(
					option_id=option.option_id,
					vessel_id=option.vessel_id,
					port_id=option.port_id,
					berth_id=option.berth_id,
					route_id=option.route_id,
					allocated_tonnes=problem.quantity_tonnes,
					objective_value=objective,
					expected_cost=cost,
					penalties=penalties,
					constraint_status=statuses,
					binding_constraints=option.binding_constraints,
					explanation=self._explain(option, penalties),
				)
			)
		ranked.sort(key=lambda item: (item.objective_value, item.option_id))
		if not ranked:
			return OptimizationResult(
				feasible=False,
				solution=None,
				alternatives=(),
				objective_value=None,
				solver_status="INFEASIBLE",
				decision_variables={"shipment_quantity_tonnes": problem.quantity_tonnes},
				hard_constraints=tuple(rejected) or ("no feasible option",),
				soft_constraints=(),
				penalties={},
				explanation="No candidate satisfies all hard constraints.",
			)
		best = ranked[0]
		return OptimizationResult(
			feasible=True,
			solution=best,
			alternatives=tuple(ranked[1 : alternatives + 1]),
			objective_value=best.objective_value,
			solver_status=self.solver_status,
			decision_variables={
				"shipment_quantity_tonnes": problem.quantity_tonnes,
				"allocated_tonnes": best.allocated_tonnes,
				"selected_option": best.option_id,
			},
			hard_constraints=tuple(
				status.name for status in best.constraint_status if status.hard
			),
			soft_constraints=tuple(
				status.name for status in best.constraint_status if not status.hard
			),
			penalties=best.penalties,
			explanation=best.explanation,
		)

	@staticmethod
	def _explain(option, penalties: dict[str, float]) -> str:
		binding = ", ".join(option.binding_constraints) or "none"
		return (
			f"Selected {option.option_id}; binding constraints: {binding}; "
			"penalties are explicit."
		)


__all__ = ["OptimizationSolver"]
