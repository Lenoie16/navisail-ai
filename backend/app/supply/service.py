"""Inventory-aware plant supply and stockout risk calculations."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InboundShipment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shipment_id: str = Field(min_length=1)
    quantity_tonnes: float = Field(gt=0)
    eta: datetime
    delay_hours: float = Field(default=0, ge=0)
    delay_probability: float = Field(default=0, ge=0, le=1)
    congestion_delay_hours: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def valid_eta(self) -> InboundShipment:
        if self.eta.tzinfo is None or self.eta.utcoffset() is None:
            raise ValueError("shipment ETA must include a timezone")
        self.eta = self.eta.astimezone(UTC)
        return self


class PlantSupplyPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plant_id: str = Field(min_length=1)
    material: str = Field(min_length=1)
    current_stock_tonnes: float = Field(ge=0)
    consumption_rate_tonnes_per_day: float = Field(gt=0)
    safety_stock_tonnes: float = Field(default=0, ge=0)
    reorder_threshold_tonnes: float = Field(default=0, ge=0)
    replenishment_tonnes_per_day: float = Field(default=0, ge=0)
    inbound_shipments: tuple[InboundShipment, ...] = ()


class SupplyProjection(BaseModel):
    plant_id: str
    material: str
    as_of: datetime
    horizon_days: int = Field(gt=0)
    projected_inventory_tonnes: float
    days_of_cover: float
    stockout_date: datetime | None
    stockout_probability: float = Field(ge=0, le=1)
    safety_margin_tonnes: float
    shipment_delay_exposure_hours: float
    continuity_acceptable: bool
    assumptions: tuple[str, ...]


class SupplyRiskEngine:
    """Project supply continuity without mutating inventory persistence or state."""

    def project(
        self,
        plan: PlantSupplyPlan,
        *,
        as_of: datetime,
        horizon_days: int = 90,
        delay_scenarios: tuple[float, ...] = (),
        stockout_probability_limit: float = 0.2,
    ) -> SupplyProjection:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must include a timezone")
        if not 0 <= stockout_probability_limit <= 1:
            raise ValueError("stockout_probability_limit must be between 0 and 1")
        current = as_of.astimezone(UTC)
        horizon = current + timedelta(days=horizon_days)
        inventory = plan.current_stock_tonnes
        consumption = plan.consumption_rate_tonnes_per_day
        events = sorted(plan.inbound_shipments, key=lambda item: item.eta)
        cursor = current
        stockout_date: datetime | None = None
        for shipment in events:
            arrival = shipment.eta + timedelta(hours=shipment.congestion_delay_hours)
            if arrival > horizon:
                break
            elapsed = max(0, (arrival - cursor).total_seconds() / 86400)
            inventory += (plan.replenishment_tonnes_per_day - consumption) * elapsed
            if inventory <= 0 and stockout_date is None:
                stockout_date = cursor + timedelta(days=max(0, inventory / consumption))
            inventory += shipment.quantity_tonnes
            cursor = arrival
        elapsed = max(0, (horizon - cursor).total_seconds() / 86400)
        inventory += (plan.replenishment_tonnes_per_day - consumption) * elapsed
        if inventory <= 0 and stockout_date is None:
            stockout_date = horizon
        cover = max(0, inventory / consumption)
        delay_exposure = sum(
            shipment.delay_hours * shipment.delay_probability + shipment.congestion_delay_hours
            for shipment in events
        )
        scenarios = delay_scenarios or tuple(
            shipment.delay_hours + shipment.congestion_delay_hours for shipment in events
        )
        breach_count = 0
        for delay in scenarios:
            delayed_inventory = self._inventory_at(plan, current, horizon, delay_hours=delay)
            if delayed_inventory < plan.safety_stock_tonnes:
                breach_count += 1
        probability = (
            breach_count / len(scenarios)
            if scenarios
            else float(inventory < plan.safety_stock_tonnes)
        )
        return SupplyProjection(
            plant_id=plan.plant_id,
            material=plan.material,
            as_of=current,
            horizon_days=horizon_days,
            projected_inventory_tonnes=inventory,
            days_of_cover=cover,
            stockout_date=stockout_date,
            stockout_probability=probability,
            safety_margin_tonnes=inventory - plan.safety_stock_tonnes,
            shipment_delay_exposure_hours=delay_exposure,
            continuity_acceptable=probability <= stockout_probability_limit
            and inventory >= plan.reorder_threshold_tonnes,
            assumptions=(
                "consumption and replenishment rates are constant",
                "inbound quantity is received at adjusted ETA",
                "stockout probability is empirical over supplied delay scenarios",
            ),
        )

    def _inventory_at(
        self, plan: PlantSupplyPlan, as_of: datetime, target: datetime, *, delay_hours: float
    ) -> float:
        inventory = plan.current_stock_tonnes
        cursor = as_of
        for index, shipment in enumerate(sorted(plan.inbound_shipments, key=lambda item: item.eta)):
            arrival = shipment.eta + timedelta(
                hours=delay_hours if index == 0 else shipment.congestion_delay_hours
            )
            if arrival > target:
                break
            elapsed = (arrival - cursor).total_seconds() / 86400
            inventory += (
                plan.replenishment_tonnes_per_day - plan.consumption_rate_tonnes_per_day
            ) * elapsed
            inventory += shipment.quantity_tonnes
            cursor = arrival
        elapsed = max(0, (target - cursor).total_seconds() / 86400)
        return (
            inventory
            + (plan.replenishment_tonnes_per_day - plan.consumption_rate_tonnes_per_day) * elapsed
        )


supply_risk_engine = SupplyRiskEngine()

__all__ = [
    "InboundShipment",
    "PlantSupplyPlan",
    "SupplyProjection",
    "SupplyRiskEngine",
    "supply_risk_engine",
]
