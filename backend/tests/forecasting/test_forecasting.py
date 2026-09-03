from datetime import UTC, datetime, timedelta

import pytest
from app.forecasting.inference.service import ForecastEngine, FreightObservation


def _history(count: int = 100) -> list[FreightObservation]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        FreightObservation(
            observed_at=start + timedelta(days=index),
            route="AU-IND-1",
            origin="AU",
            destination="IN",
            vessel_class="Panamax",
            rate=100 + index,
            currency="USD",
            unit="USD/tonne",
        )
        for index in range(count)
    ]


def test_forecast_supports_all_requested_horizons_and_input_snapshot() -> None:
    engine = ForecastEngine()
    history = _history()

    for horizon in (7, 15, 30, 90):
        result = engine.forecast(
            history,
            route="AU-IND-1",
            vessel_class="Panamax",
            horizon_days=horizon,
            model="rolling_mean",
        )
        assert result.horizon_days == horizon
        assert result.input_snapshot
        assert result.model_version == "freight-baselines-v1"
        assert result.p10 <= result.p25 <= result.p50 <= result.p75 <= result.p90
        assert result.p50 == result.point_forecast
        assert result.interval_width == result.p90 - result.p10
        assert result.model_confidence >= result.decision_confidence


def test_as_of_excludes_future_information() -> None:
    engine = ForecastEngine()
    history = _history()
    as_of = history[30].observed_at

    result = engine.forecast(
        history,
        route="AU-IND-1",
        vessel_class="Panamax",
        horizon_days=7,
        model="naive",
        as_of=as_of,
    )

    assert result.point_forecast == history[30].rate
    assert result.forecast_date == (as_of + timedelta(days=7)).date()
    assert result.confidence_metadata["history_points"] == 31


def test_backtest_compares_models_against_naive_without_future_leakage() -> None:
    metrics = ForecastEngine().backtest(_history(), horizon_days=7)

    assert set(metrics) == {"naive", "rolling_mean", "exponential_smoothing"}
    assert metrics["naive"].baseline_mae == metrics["naive"].mae
    assert metrics["rolling_mean"].observations > 0
    assert metrics["naive"].coverage_p10_p90 is not None


def test_calibration_reports_horizon_coverage_and_data_confidence() -> None:
    engine = ForecastEngine()
    history = [item.model_copy(update={"quality_score": 0.8}) for item in _history()]

    result = engine.forecast(
        history,
        route="AU-IND-1",
        vessel_class="Panamax",
        horizon_days=7,
        model="naive",
    )
    calibration = engine.calibration(history, horizon_days=7)

    assert result.data_confidence == 0.8
    assert result.decision_confidence == result.model_confidence * 0.8
    assert calibration["status"] == "calibrated"
    assert calibration["observations"] > 20
    assert calibration["coverage_p10_p90"] == 1.0


def test_invalid_horizon_and_missing_series_are_rejected() -> None:
    engine = ForecastEngine()
    with pytest.raises(ValueError, match="horizon_days"):
        engine.forecast(
            _history(), route="AU-IND-1", vessel_class="Panamax", horizon_days=8
        )
    with pytest.raises(ValueError, match="no historical"):
        engine.forecast(
            _history(), route="missing", vessel_class="Panamax", horizon_days=7
        )