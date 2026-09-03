"""Multi-voyage procurement and charter strategy optimization."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

StrategyName = Literal["Spot", "COA", "Time Charter", "Hybrid"]
MarketCondition = Literal["stable", "volatile", "rising", "falling"]


class VoyageDemand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    voyage_id: str = Field(min_length=1)
    volume_tonnes: float = Field(gt=0)
    spot_p10: float = Field(gt=0)
    spot_p50: float = Field(gt=0)
    spot_p90: float = Field(gt=0)
    coa_rate: float = Field(gt=0)
    time_charter_rate: float = Field(gt=0)
    spot_reliability: float = Field(default=0.8, ge=0, le=1)
    coa_reliability: float = Field(default=0.95, ge=0, le=1)
    time_charter_reliability: float = Field(default=0.98, ge=0, le=1)

    @model_validator(mode="after")
    def ordered_spot_quantiles(self) -> VoyageDemand:
        if not self.spot_p10 <= self.spot_p50 <= self.spot_p90:
            raise ValueError("spot quantiles must be ordered")
        return self


class StrategyConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_tolerance: float = Field(default=1, ge=0, le=1)
    inventory_pressure: float = Field(default=0, ge=0, le=1)
    minimum_coa_share: float = Field(default=0, ge=0, le=1)
    maximum_time_charter_share: float = Field(default=1, ge=0, le=1)
    strategic_flexibility_floor: float = Field(default=0, ge=0, le=1)


class StrategyAlternative(BaseModel):
    strategy: StrategyName
    volume_allocation: dict[str, float]
    expected_cost: float = Field(ge=0)
    risk: float = Field(ge=0, le=1)
    schedule_reliability: float = Field(ge=0, le=1)
    downside_exposure: float = Field(ge=0)
    flexibility: float = Field(ge=0, le=1)
    objective_value: float = Field(ge=0)
    justification: str


class StrategyOptimizationResult(BaseModel):
    recommended_strategy: StrategyName
    recommended_allocation: dict[str, float]
    expected_cost: float
    alternatives: tuple[StrategyAlternative, ...]
    market_condition: MarketCondition
    total_volume_tonnes: float
    explanation: str


class StrategyOptimizer:
    """Rank procurement mixes across all supplied planned voyages."""

    def optimize(
        self,
        voyages: Iterable[VoyageDemand],
        *,
        market_condition: MarketCondition = "stable",
        constraints: StrategyConstraints | None = None,
    ) -> StrategyOptimizationResult:
        demand = tuple(voyages)
        if not demand:
            raise ValueError("at least one voyage is required")
        limits = (
            constraints
            if isinstance(constraints, StrategyConstraints)
            else StrategyConstraints.model_validate(constraints or {})
        )
        total_volume = sum(voyage.volume_tonnes for voyage in demand)
        allocations = self._allocations(limits)
        alternatives = tuple(
            self._evaluate(allocation, demand, market_condition, limits)
            for allocation in allocations
        )
        feasible = [item for item in alternatives if item.risk <= limits.risk_tolerance]
        if not feasible:
            raise ValueError("no procurement strategy satisfies risk tolerance")
        ranked = sorted(feasible, key=lambda item: (item.objective_value, item.strategy))
        best = ranked[0]
        return StrategyOptimizationResult(
            recommended_strategy=best.strategy,
            recommended_allocation=best.volume_allocation,
            expected_cost=best.expected_cost,
            alternatives=tuple(ranked),
            market_condition=market_condition,
            total_volume_tonnes=total_volume,
            explanation=(
                f"{best.strategy} minimizes expected cost plus explicit risk and "
                "inventory-pressure penalties for the supplied voyages."
            ),
        )

    def _allocations(self, constraints: StrategyConstraints) -> list[dict[str, float]]:
        allocations = [
            {"Spot": 1.0, "COA": 0.0, "Time Charter": 0.0},
            {"Spot": 0.0, "COA": 1.0, "Time Charter": 0.0},
            {"Spot": 0.0, "COA": 0.0, "Time Charter": 1.0},
        ]
        allocations = [
            allocation
            for allocation in allocations
            if allocation["COA"] >= constraints.minimum_coa_share
            and allocation["Time Charter"] <= constraints.maximum_time_charter_share
        ]
        for spot_steps in range(11):
            for coa_steps in range(11 - spot_steps):
                time_steps = 10 - spot_steps - coa_steps
                allocation = {
                    "Spot": spot_steps / 10,
                    "COA": coa_steps / 10,
                    "Time Charter": time_steps / 10,
                }
                if (
                    allocation["COA"] >= constraints.minimum_coa_share
                    and allocation["Time Charter"] <= constraints.maximum_time_charter_share
                ):
                    allocations.append(allocation)
        return allocations

    def _evaluate(
        self,
        allocation: dict[str, float],
        voyages: tuple[VoyageDemand, ...],
        market: MarketCondition,
        constraints: StrategyConstraints,
    ) -> StrategyAlternative:
        market_multiplier = {
            "stable": 1.0,
            "volatile": 1.0,
            "rising": 1.15,
            "falling": 0.85,
        }[market]
        totals = {"Spot": 0.0, "COA": 0.0, "Time Charter": 0.0}
        downside = 0.0
        downside_multiplier = {
            "stable": 0.01,
            "volatile": 0.5,
            "rising": 0.02,
            "falling": 0.01,
        }[market]
        reliability = 0.0
        for voyage in voyages:
            spot_cost = voyage.spot_p50 * market_multiplier
            coa_cost = voyage.coa_rate
            tc_cost = voyage.time_charter_rate
            volume = voyage.volume_tonnes
            totals["Spot"] += spot_cost * volume
            totals["COA"] += coa_cost * volume
            totals["Time Charter"] += tc_cost * volume
            downside += (
                allocation["Spot"]
                * (voyage.spot_p90 - voyage.spot_p50)
                * volume
                * downside_multiplier
            )
            reliability += volume * (
                allocation["Spot"] * voyage.spot_reliability
                + allocation["COA"] * voyage.coa_reliability
                + allocation["Time Charter"] * voyage.time_charter_reliability
            )
        total_volume = sum(voyage.volume_tonnes for voyage in voyages)
        expected_cost = sum(allocation[name] * totals[name] for name in totals)
        schedule_reliability = reliability / total_volume
        risk = min(1.0, (downside / max(expected_cost, 1)) + (1 - schedule_reliability))
        flexibility = (
            allocation["Spot"]
            + 0.4 * allocation["COA"]
            + 0.2 * allocation["Time Charter"]
        )
        if flexibility < constraints.strategic_flexibility_floor:
            risk = min(1.0, risk + constraints.strategic_flexibility_floor - flexibility)
        inventory_penalty = (
            constraints.inventory_pressure
            * (1 - schedule_reliability)
            * expected_cost
        )
        objective = expected_cost + downside + inventory_penalty
        strategy = self._strategy_name(allocation)
        return StrategyAlternative(
            strategy=strategy,
            volume_allocation=allocation,
            expected_cost=expected_cost,
            risk=risk,
            schedule_reliability=schedule_reliability,
            downside_exposure=downside,
            flexibility=flexibility,
            objective_value=objective,
            justification=(
                f"{strategy} allocates {allocation['Spot']:.0%} spot, "
                f"{allocation['COA']:.0%} COA, and {allocation['Time Charter']:.0%} time charter."
            ),
        )

    @staticmethod
    def _strategy_name(allocation: dict[str, float]) -> StrategyName:
        active = [name for name, share in allocation.items() if share > 0]
        if len(active) > 1:
            return "Hybrid"
        return active[0]  # type: ignore[return-value]


strategy_optimizer = StrategyOptimizer()

__all__ = [
    "MarketCondition",
    "StrategyAlternative",
    "StrategyConstraints",
    "StrategyOptimizationResult",
    "StrategyOptimizer",
    "StrategyName",
    "VoyageDemand",
    "strategy_optimizer",
]