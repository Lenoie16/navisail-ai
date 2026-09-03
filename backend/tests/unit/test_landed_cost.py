from datetime import UTC, datetime

import pytest
from app.landed_cost.service import LandedCostEngine
from app.schemas.cost import CostComponentInput, FXQuote, ScenarioAdjustment


def test_arithmetic_and_unit_conversion() -> None:
    result = LandedCostEngine().calculate(
        [
            CostComponentInput(
                component="freight",
                rate=10,
                currency="USD",
                unit="per_tonne",
                quantity=999,
                source="contract",
            ),
            CostComponentInput(
                component="handling",
                rate=0.02,
                currency="USD",
                unit="per_kg",
                source="tariff",
            ),
        ],
        quantity_tonnes=100,
        target_currency="USD",
    )

    assert result.expected_landed_cost == 3000
    assert result.cost_per_tonne == 30
    assert result.total_voyage_cost == 3000
    assert "USD/tonne" in result.components[0].formula


def test_currency_conversion_records_fx_metadata() -> None:
    quote = FXQuote(
        base_currency="USD",
        quote_currency="EUR",
        rate=0.9,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        source="fx-feed",
        source_status="LIVE",
    )
    result = LandedCostEngine().calculate(
        [CostComponentInput(component="freight", rate=100, currency="USD", source="market")],
        quantity_tonnes=1,
        target_currency="EUR",
        fx_quotes=[quote],
    )

    assert result.expected_landed_cost == 90
    assert result.fx_source == "fx-feed"
    assert result.fx_source_status == "LIVE"
    assert result.fx_timestamp == quote.timestamp


def test_empty_components_and_delay_scenario() -> None:
    result = LandedCostEngine().calculate(
        [],
        quantity_tonnes=100,
        target_currency="USD",
        scenario=ScenarioAdjustment(
            name="moderate delay",
            delay_hours=10,
            delay_cost_per_hour=25,
            disruption_cost=100,
            inventory_days=2,
            inventory_cost_per_tonne_day=0.5,
        ),
    )

    assert result.expected_landed_cost == 450
    assert result.risk_adjusted_landed_cost == 450
    assert {item.component for item in result.components} == {
        "delay_cost",
        "disruption_cost",
        "inventory_carrying_cost",
    }


def test_risk_multiplier_and_missing_fx_are_explicit() -> None:
    with pytest.raises(ValueError, match="missing FX"):
        LandedCostEngine().calculate(
            [CostComponentInput(component="freight", rate=10, currency="USD", source="market")],
            quantity_tonnes=1,
            target_currency="EUR",
        )
    result = LandedCostEngine().calculate(
        [
            CostComponentInput(
                component="freight", rate=100, currency="USD", source="market", risk_multiplier=1.2
            )
        ],
        quantity_tonnes=1,
        target_currency="USD",
    )
    assert result.expected_landed_cost == 100
    assert result.risk_adjusted_landed_cost == 120