"""Optimization service facade."""

import json

from app.core.performance import BoundedTTLCache, measure, metrics_store
from app.optimization.models import OptimizationProblem, OptimizationResult
from app.optimization.solver import OptimizationSolver


class OptimizationService:
	def __init__(self, solver: OptimizationSolver | None = None) -> None:
		self.solver = solver or OptimizationSolver()
		self._cache = BoundedTTLCache()

	def optimize(self, problem: OptimizationProblem) -> OptimizationResult:
		key = json.dumps(problem.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
		cached = self._cache.get(key)
		if isinstance(cached, OptimizationResult):
			return cached.model_copy(deep=True)
		with measure("optimization", metrics_store):
			result = self.solver.solve(problem)
		self._cache.set(key, result.model_copy(deep=True))
		return result

	def clear_cache(self) -> None:
		self._cache.clear()


optimization_service = OptimizationService()

__all__ = ["OptimizationService", "optimization_service"]
