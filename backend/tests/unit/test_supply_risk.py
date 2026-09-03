from datetime import UTC, datetime, timedelta

from app.supply.service import InboundShipment, PlantSupplyPlan, SupplyRiskEngine

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _plan(**overrides: object) -> PlantSupplyPlan:
    values: dict[str, object] = {
        "plant_id": "plant-1",
        "material": "ore",
        "current_stock_tonnes": 1_000,
        "consumption_rate_tonnes_per_day": 100,
        "safety_stock_tonnes": 200,
        "reorder_threshold_tonnes": 200,
        "inbound_shipments": (
            InboundShipment(
                shipment_id="ship-1",
                quantity_tonnes=2_000,
                eta=NOW + timedelta(days=5),
            ),
        ),
    }
    values.update(overrides)
    return PlantSupplyPlan(**values)


def test_projection_reports_cover_and_inbound_replenishment() -> None:
    result = SupplyRiskEngine().project(_plan(), as_of=NOW, horizon_days=10)

    assert result.projected_inventory_tonnes == 2_000
    assert result.days_of_cover == 20
    assert result.stockout_probability == 0
    assert result.continuity_acceptable is True


def test_delay_scenarios_increase_stockout_risk_and_exposure() -> None:
    plan = _plan(current_stock_tonnes=300, safety_stock_tonnes=200)
    on_time = SupplyRiskEngine().project(plan, as_of=NOW, horizon_days=10, delay_scenarios=(0,))
    delayed = SupplyRiskEngine().project(plan, as_of=NOW, horizon_days=10, delay_scenarios=(0, 240))

    assert delayed.stockout_probability > on_time.stockout_probability
    assert delayed.shipment_delay_exposure_hours == on_time.shipment_delay_exposure_hours
    assert delayed.continuity_acceptable is False


def test_optimizer_rejects_cheapest_option_that_breaks_continuity() -> None:
    from app.optimization.models import OptimizationOption, OptimizationProblem
    from app.optimization.service import OptimizationService

    options = (
        OptimizationOption(
            option_id="cheap-risky",
            vessel_id="v1",
            port_id="p1",
            berth_id="b1",
            route_id="r1",
            available_at=NOW,
            capacity_tonnes=1_000,
            cost_per_tonne=5,
            stockout_probability=0.8,
            continuity_acceptable=False,
        ),
        OptimizationOption(
            option_id="acceptable",
            vessel_id="v2",
            port_id="p2",
            berth_id="b2",
            route_id="r2",
            available_at=NOW,
            capacity_tonnes=1_000,
            cost_per_tonne=10,
        ),
    )
    problem = OptimizationProblem(
        shipment_id="ship-1",
        quantity_tonnes=500,
        booking_deadline=NOW,
        inventory_available_tonnes=500,
        options=options,
    )

    result = OptimizationService().optimize(problem)

    assert result.solution is not None
    assert result.solution.option_id == "acceptable"
