"""Chronological, reproducible evaluation helpers."""

from typing import Any

from app.mlops.drift import mean_absolute_error


def chronological_validation(
    actuals: list[float], predictions: list[float], *, benchmark: list[float] | None = None
) -> dict[str, Any]:
    if len(actuals) != len(predictions) or len(actuals) < 2:
        raise ValueError("chronological validation requires equal series with at least two observations")
    metrics: dict[str, Any] = {
        "observations": len(actuals),
        "mae": mean_absolute_error(predictions, actuals),
        "residuals": [actual - predicted for actual, predicted in zip(actuals, predictions)],
    }
    if benchmark is not None:
        if len(benchmark) != len(actuals):
            raise ValueError("benchmark must match actual series length")
        metrics["benchmark_mae"] = mean_absolute_error(benchmark, actuals)
        metrics["improvement_vs_benchmark"] = metrics["benchmark_mae"] - metrics["mae"]
    return metrics


def calibration(actuals: list[float], lower: list[float], upper: list[float]) -> dict[str, float]:
    if not actuals or len(actuals) != len(lower) or len(actuals) != len(upper):
        raise ValueError("calibration series must have equal non-zero length")
    coverage = sum(lo <= actual <= hi for actual, lo, hi in zip(actuals, lower, upper)) / len(actuals)
    return {"coverage": coverage, "mean_interval_width": sum(hi - lo for lo, hi in zip(lower, upper)) / len(actuals)}
