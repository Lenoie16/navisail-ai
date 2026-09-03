from datetime import UTC, datetime, timedelta

from app.risk.regime import MarketRegimeDetector, MarketSignal


def _signal(day: int, rate: float, **overrides: object) -> MarketSignal:
    values: dict[str, object] = {
        "observed_at": datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=day),
        "freight_rate": rate,
        "volume": 100,
        "vessel_availability": 0.9,
        "fuel_price": 500,
    }
    values.update(overrides)
    return MarketSignal(**values)


def test_injected_shocks_are_detected_with_drivers_and_hints() -> None:
    signals = [
        _signal(0, 100),
        _signal(1, 102),
        _signal(2, 130, congestion_score=0.9, vessel_availability=0.2, fuel_price=700),
        _signal(3, 110, operational_status="outage"),
    ]

    result = MarketRegimeDetector().detect(signals)

    assert result.regime in {"disrupted", "shock/recovery"}
    assert {shock.shock_type for shock in result.shocks} >= {
        "freight spike",
        "congestion shock",
        "fuel shock",
        "supply reduction",
        "port outage",
    }
    assert result.risk_scenario_hint == "severe"
    assert result.forecast_market_condition in {"volatile", "falling"}


def test_known_directional_and_stable_series_classify() -> None:
    detector = MarketRegimeDetector()
    rising = detector.detect([_signal(index, 100 + index * 5) for index in range(5)])
    stable = detector.detect([_signal(index, 100) for index in range(5)])

    assert rising.regime == "rising"
    assert stable.regime == "stable"
    assert stable.shocks == ()
