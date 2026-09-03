"""Seeded Monte Carlo simulation for logistics cost and delay risk."""

from __future__ import annotations

import math
import random
import json
from collections.abc import Iterable

from app.risk.scenarios import RiskScenario
from pydantic import BaseModel, ConfigDict, Field
from app.core.performance import BoundedTTLCache, measure, metrics_store


class SimulationAlternative(BaseModel):
	model_config = ConfigDict(extra="forbid")

	alternative_id: str = Field(min_length=1)
	base_cost: float = Field(ge=0)
	base_delay_hours: float = Field(default=0, ge=0)
	inventory_breach_threshold_hours: float = Field(default=24, ge=0)
	cost_threshold: float = Field(default=0, ge=0)
	freight_exposure: float = Field(default=1, ge=0)
	fuel_exposure: float = Field(default=0, ge=0)
	fx_exposure: float = Field(default=0, ge=0)


class SimulationOutput(BaseModel):
	alternative_id: str
	simulations: int = Field(gt=0)
	seed: int
	scenario: str
	p10: float
	p50: float
	p90: float
	mean: float
	variance: float = Field(ge=0)
	cvar_90: float
	probability_of_delay: float = Field(ge=0, le=1)
	probability_exceeding_cost_threshold: float = Field(ge=0, le=1)
	probability_inventory_breach: float = Field(ge=0, le=1)
	mean_delay_hours: float = Field(ge=0)


class MonteCarloEngine:
	"""Simulate alternatives using common random numbers for fair comparison."""

	def __init__(self) -> None:
		self._cache = BoundedTTLCache()

	def simulate(
		self,
		alternatives: Iterable[SimulationAlternative],
		*,
		scenario: RiskScenario,
		simulations: int = 10_000,
		seed: int = 0,
	) -> list[SimulationOutput]:
		if simulations <= 0:
			raise ValueError("simulations must be positive")
		items = tuple(alternatives)
		if not items:
			raise ValueError("at least one alternative is required")
		key = json.dumps(
			{
				"alternatives": [item.model_dump(mode="json") for item in items],
				"scenario": scenario.model_dump(mode="json"),
				"simulations": simulations,
				"seed": seed,
			},
			sort_keys=True,
			separators=(",", ":"),
		)
		cached = self._cache.get(key)
		if isinstance(cached, list):
			return [item.model_copy(deep=True) for item in cached]
		streams = [self._draws(scenario, simulations, seed)]
		draws = streams[0]
		with measure("monte_carlo", metrics_store):
			result = [self._evaluate(item, scenario, draws, simulations, seed) for item in items]
		self._cache.set(key, [item.model_copy(deep=True) for item in result])
		return result

	def compare(
		self,
		alternatives: Iterable[SimulationAlternative],
		*,
		scenario: RiskScenario,
		simulations: int = 10_000,
		seed: int = 0,
	) -> dict[str, SimulationOutput]:
		return {
			output.alternative_id: output
			for output in self.simulate(
				alternatives,
				scenario=scenario,
				simulations=simulations,
				seed=seed,
			)
		}

	def clear_cache(self) -> None:
		self._cache.clear()

	@staticmethod
	def _draws(
		scenario: RiskScenario, simulations: int, seed: int
	) -> list[dict[str, float | bool]]:
		rng = random.Random(seed)
		draws: list[dict[str, float | bool]] = []
		for _ in range(simulations):
			draws.append(
				{
					"freight": rng.gauss(0, scenario.freight_volatility),
					"fuel": rng.gauss(0, scenario.fuel_volatility),
					"fx": rng.gauss(0, scenario.fx_volatility),
					"congestion": rng.random() < scenario.congestion_probability,
					"weather": rng.random() < scenario.weather_probability,
					"failure": rng.random() < scenario.vessel_failure_probability,
					"outage": rng.random() < scenario.port_outage_probability,
				}
			)
		return draws

	@staticmethod
	def _evaluate(
		alternative: SimulationAlternative,
		scenario: RiskScenario,
		draws: list[dict[str, float | bool]],
		simulations: int,
		seed: int,
	) -> SimulationOutput:
		outcomes: list[float] = []
		delays: list[float] = []
		for draw in draws:
			delay = alternative.base_delay_hours + scenario.operational_delay_hours
			if draw["congestion"]:
				delay += scenario.waiting_hours
			if draw["weather"]:
				delay += scenario.operational_delay_hours
			if draw["failure"] or draw["outage"]:
				delay += scenario.waiting_hours * 2
			disruption = scenario.disruption_cost if draw["failure"] or draw["outage"] else 0
			cost = alternative.base_cost * (
				1
				+ alternative.freight_exposure * float(draw["freight"])
				+ alternative.fuel_exposure * float(draw["fuel"])
				+ alternative.fx_exposure * float(draw["fx"])
			)
			outcomes.append(max(0, cost + delay * 100 + disruption))
			delays.append(delay)
		ordered = sorted(outcomes)
		p10 = _quantile(ordered, 0.1)
		p50 = _quantile(ordered, 0.5)
		p90 = _quantile(ordered, 0.9)
		mean = sum(outcomes) / simulations
		variance = sum((value - mean) ** 2 for value in outcomes) / simulations
		tail = [value for value in ordered if value >= p90]
		return SimulationOutput(
			alternative_id=alternative.alternative_id,
			simulations=simulations,
			seed=seed,
			scenario=scenario.name,
			p10=p10,
			p50=p50,
			p90=p90,
			mean=mean,
			variance=variance,
			cvar_90=sum(tail) / len(tail),
			probability_of_delay=(
				sum(value > alternative.base_delay_hours for value in delays) / simulations
			),
			probability_exceeding_cost_threshold=(
				sum(value > alternative.cost_threshold for value in outcomes) / simulations
				if alternative.cost_threshold
				else 0
			),
			probability_inventory_breach=sum(
				value > alternative.inventory_breach_threshold_hours for value in delays
			)
			/ simulations,
			mean_delay_hours=sum(delays) / simulations,
		)


def _quantile(values: list[float], level: float) -> float:
	position = (len(values) - 1) * level
	lower, upper = math.floor(position), math.ceil(position)
	if lower == upper:
		return values[lower]
	return values[lower] + (values[upper] - values[lower]) * (position - lower)


monte_carlo_engine = MonteCarloEngine()

__all__ = [
	"MonteCarloEngine",
	"SimulationAlternative",
	"SimulationOutput",
	"monte_carlo_engine",
]
