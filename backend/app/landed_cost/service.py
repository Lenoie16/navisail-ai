"""Risk-aware landed-cost calculation with explicit assumptions."""

from __future__ import annotations

from collections.abc import Iterable

from app.schemas.cost import (
    CostComponent,
    CostComponentInput,
    FXQuote,
    LandedCostResult,
    ScenarioAdjustment,
)


class LandedCostEngine:
    """Calculate costs without hiding units, sources, or FX assumptions."""

    def calculate(
        self,
        components: Iterable[CostComponentInput],
        *,
        quantity_tonnes: float,
        target_currency: str,
        fx_quotes: Iterable[FXQuote] = (),
        scenario: ScenarioAdjustment | None = None,
    ) -> LandedCostResult:
        if quantity_tonnes <= 0:
            raise ValueError("quantity_tonnes must be positive")
        target = target_currency.upper()
        quotes = list(fx_quotes)
        adjustment = scenario or ScenarioAdjustment()
        converted: list[CostComponent] = []
        expected_total = 0.0
        risk_total = 0.0
        latest_quote: FXQuote | None = None
        for item in components:
            amount = self._amount(item, quantity_tonnes)
            converted_value, quote = self._convert(amount, item.currency, target, quotes)
            latest_quote = quote or latest_quote
            expected_total += converted_value
            risk_value = converted_value * item.risk_multiplier
            risk_total += risk_value
            assumptions = item.assumptions + (f"unit basis: {item.unit}",)
            if item.risk_multiplier > 1:
                assumptions += (f"component risk multiplier: {item.risk_multiplier}",)
            converted.append(
                CostComponent(
                    component=item.component,
                    formula=self._formula(item, quantity_tonnes, target, quote),
                    value=risk_value,
                    currency=target,
                    source=item.source,
                    assumptions=assumptions,
                )
            )
        derived = self._scenario_components(adjustment, quantity_tonnes, target)
        converted.extend(derived)
        expected_total += sum(item.value for item in derived)
        risk_total = risk_total * adjustment.risk_multiplier + sum(item.value for item in derived)
        return LandedCostResult(
            components=tuple(converted),
            expected_landed_cost=expected_total,
            risk_adjusted_landed_cost=risk_total,
            cost_per_tonne=risk_total / quantity_tonnes,
            total_voyage_cost=expected_total,
            currency=target,
            quantity_tonnes=quantity_tonnes,
            fx_timestamp=latest_quote.timestamp if latest_quote else None,
            fx_source=latest_quote.source if latest_quote else None,
            fx_source_status=latest_quote.source_status if latest_quote else None,
            scenario=adjustment.name,
        )

    @staticmethod
    def _amount(item: CostComponentInput, quantity_tonnes: float) -> float:
        if item.unit == "per_tonne":
            return item.rate * quantity_tonnes
        if item.unit == "per_kg":
            return item.rate * quantity_tonnes * 1000
        return item.rate * item.quantity

    def _convert(
        self, amount: float, source: str, target: str, quotes: list[FXQuote]
    ) -> tuple[float, FXQuote | None]:
        source = source.upper()
        if source == target:
            return amount, None
        for quote in quotes:
            if quote.base_currency.upper() == source and quote.quote_currency.upper() == target:
                return amount * quote.rate, quote
            if quote.base_currency.upper() == target and quote.quote_currency.upper() == source:
                return amount / quote.rate, quote
        raise ValueError(f"missing FX quote from {source} to {target}")

    @staticmethod
    def _formula(
        item: CostComponentInput, quantity_tonnes: float, target: str, quote: FXQuote | None
    ) -> str:
        if item.unit == "per_tonne":
            basis = f"{item.rate} {item.currency}/tonne * {quantity_tonnes} tonnes"
        elif item.unit == "per_kg":
            basis = f"{item.rate} {item.currency}/kg * {quantity_tonnes * 1000} kg"
        else:
            basis = f"{item.rate} {item.currency} * {item.quantity}"
        if quote:
            return f"({basis}) converted to {target} at {quote.rate} ({quote.source})"
        return basis

    @staticmethod
    def _scenario_components(
        scenario: ScenarioAdjustment, quantity_tonnes: float, currency: str
    ) -> list[CostComponent]:
        components: list[CostComponent] = []
        if scenario.delay_hours and scenario.delay_cost_per_hour:
            value = scenario.delay_hours * scenario.delay_cost_per_hour
            components.append(
                CostComponent(
                    component="delay_cost",
                    formula=(
                        f"{scenario.delay_hours} hours * "
                        f"{scenario.delay_cost_per_hour} {currency}/hour"
                    ),
                    value=value,
                    currency=currency,
                    source="scenario",
                    assumptions=(f"scenario: {scenario.name}",),
                )
            )
        if scenario.disruption_cost:
            components.append(
                CostComponent(
                    component="disruption_cost",
                    formula=f"scenario disruption cost: {scenario.disruption_cost} {currency}",
                    value=scenario.disruption_cost,
                    currency=currency,
                    source="scenario",
                    assumptions=(f"scenario: {scenario.name}",),
                )
            )
        if scenario.inventory_days and scenario.inventory_cost_per_tonne_day:
            value = (
                scenario.inventory_days
                * scenario.inventory_cost_per_tonne_day
                * quantity_tonnes
            )
            components.append(
                CostComponent(
                    component="inventory_carrying_cost",
                    formula=(
                        f"{scenario.inventory_days} days * "
                        f"{scenario.inventory_cost_per_tonne_day} {currency}/tonne/day * "
                        f"{quantity_tonnes} tonnes"
                    ),
                    value=value,
                    currency=currency,
                    source="scenario",
                    assumptions=(f"scenario: {scenario.name}",),
                )
            )
        return components


landed_cost_engine = LandedCostEngine()

__all__ = ["LandedCostEngine", "landed_cost_engine"]