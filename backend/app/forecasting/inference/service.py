"""Reproducible freight forecasting and rolling-origin evaluation."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.core.performance import BoundedTTLCache, measure, metrics_store

ForecastModel = Literal["naive", "rolling_mean", "exponential_smoothing", "auto"]
CalibrationStatus = Literal["calibrated", "insufficient_history"]
SUPPORTED_HORIZONS = (7, 15, 30, 90)


class FreightObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observed_at: datetime
    route: str = Field(min_length=1)
    origin: str | None = None
    destination: str | None = None
    vessel_class: str = Field(min_length=1)
    rate: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    unit: str = Field(min_length=1)
    quality_score: float = Field(default=1, ge=0, le=1)
    features: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_timestamp(self) -> FreightObservation:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must include a timezone")
        self.observed_at = self.observed_at.astimezone(UTC)
        return self


class ForecastResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    point_forecast: float = Field(gt=0)
    p10: float = Field(gt=0)
    p25: float = Field(gt=0)
    p50: float = Field(gt=0)
    p75: float = Field(gt=0)
    p90: float = Field(gt=0)
    interval_width: float = Field(ge=0)
    forecast_date: date
    horizon_days: int
    route: str
    vessel_class: str
    model_version: str
    model: str
    input_snapshot: str
    confidence: float = Field(ge=0, le=1)
    model_confidence: float = Field(ge=0, le=1)
    data_confidence: float = Field(ge=0, le=1)
    decision_confidence: float = Field(ge=0, le=1)
    calibration_status: CalibrationStatus
    data_quality: float = Field(ge=0, le=1)
    confidence_metadata: dict[str, float | int | str]


class EvaluationMetrics(BaseModel):
    model: str
    horizon_days: int
    observations: int = Field(ge=0)
    mae: float | None = Field(default=None, ge=0)
    rmse: float | None = Field(default=None, ge=0)
    baseline_mae: float | None = Field(default=None, ge=0)
    improvement_over_naive: float | None = None
    residual_count: int = Field(default=0, ge=0)
    coverage_p10_p90: float | None = Field(default=None, ge=0, le=1)


class ForecastEngine:
    """Forecast route and vessel-class freight conditions using history only."""

    model_version = "freight-baselines-v1"

    def __init__(self) -> None:
        self._cache = BoundedTTLCache()

    def features(self, observations: Iterable[FreightObservation]) -> list[dict[str, float | str]]:
        """Build causal features; each row only uses observations at or before itself."""

        ordered = sorted(observations, key=lambda item: item.observed_at)
        rows: list[dict[str, float | str]] = []
        for index, item in enumerate(ordered):
            history = [sample.rate for sample in ordered[: index + 1]]
            window = history[-7:]
            mean = sum(window) / len(window)
            rows.append(
                {
                    "observed_at": item.observed_at.isoformat(),
                    "route": item.route,
                    "vessel_class": item.vessel_class,
                    "rate": item.rate,
                    "rolling_mean_7": mean,
                    "trend": item.rate - history[0],
                    "volatility_7": math.sqrt(
                        sum((value - mean) ** 2 for value in window) / len(window)
                    ),
                    **item.features,
                }
            )
        return rows

    def clear_cache(self) -> None:
        self._cache.clear()

    def forecast(
        self,
        observations: Iterable[FreightObservation],
        *,
        route: str,
        vessel_class: str,
        horizon_days: int,
        model: ForecastModel = "auto",
        as_of: datetime | None = None,
    ) -> ForecastResult:
        if horizon_days not in SUPPORTED_HORIZONS:
            raise ValueError(f"horizon_days must be one of {SUPPORTED_HORIZONS}")
        history = sorted(
            (
                item
                for item in observations
                if item.route == route
                and item.vessel_class == vessel_class
                and (as_of is None or item.observed_at <= as_of.astimezone(UTC))
            ),
            key=lambda item: item.observed_at,
        )
        if not history:
            raise ValueError("no historical observations for route and vessel class")
        cache_key = json.dumps(
            {
                "version": self.model_version,
                "route": route,
                "vessel_class": vessel_class,
                "horizon_days": horizon_days,
                "model": model,
                "as_of": as_of.isoformat() if as_of else None,
                "history": [item.model_dump(mode="json") for item in history],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        cached = self._cache.get(cache_key)
        if isinstance(cached, ForecastResult):
            return cached.model_copy(deep=True)
        with measure("forecast", metrics_store):
            result = self._forecast_uncached(
                history,
                route=route,
                vessel_class=vessel_class,
                horizon_days=horizon_days,
                model=model,
                as_of=as_of,
            )
        self._cache.set(cache_key, result.model_copy(deep=True))
        return result

    def _forecast_uncached(
        self,
        history: list[FreightObservation],
        *,
        route: str,
        vessel_class: str,
        horizon_days: int,
        model: ForecastModel,
        as_of: datetime | None,
    ) -> ForecastResult:
        selected = model
        if selected == "auto":
            scores = self.backtest(history, horizon_days=horizon_days)
            selected = min(scores, key=lambda name: scores[name].mae or math.inf)
        values = [item.rate for item in history]
        point = self._predict(values, selected)
        last_at = history[-1].observed_at
        forecast_at = (as_of.astimezone(UTC) if as_of else last_at) + timedelta(days=horizon_days)
        snapshot_payload = [item.model_dump(mode="json") for item in history]
        snapshot = hashlib.sha256(
            json.dumps(snapshot_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        volatility = self._volatility(values)
        residuals = self._residuals(history, horizon_days, selected)
        residual_quantiles = self._residual_quantiles(residuals, volatility, horizon_days)
        residual_median = residual_quantiles[0.5]
        quantiles = {
            level: max(0.01, point + residual_quantiles[quantile] - residual_median)
            for level, quantile in (
                ("p10", 0.1),
                ("p25", 0.25),
                ("p75", 0.75),
                ("p90", 0.9),
            )
        }
        quantiles["p50"] = point
        model_confidence = max(
            0.1, min(0.99, len(values) / 30 * (1 / (1 + volatility / point)))
        )
        data_confidence = sum(item.quality_score for item in history) / len(history)
        decision_confidence = model_confidence * data_confidence
        calibration_status: CalibrationStatus = (
            "calibrated" if len(residuals) >= 20 else "insufficient_history"
        )
        return ForecastResult(
            point_forecast=point,
            **quantiles,
            interval_width=quantiles["p90"] - quantiles["p10"],
            forecast_date=forecast_at.date(),
            horizon_days=horizon_days,
            route=route,
            vessel_class=vessel_class,
            model_version=self.model_version,
            model=selected,
            input_snapshot=snapshot,
            confidence=model_confidence,
            model_confidence=model_confidence,
            data_confidence=data_confidence,
            decision_confidence=decision_confidence,
            calibration_status=calibration_status,
            data_quality=data_confidence,
            confidence_metadata={
                "history_points": len(values),
                "residual_points": len(residuals),
                "historical_volatility": volatility,
                "selection": "backtest_mae" if model == "auto" else "requested",
            },
        )

    def backtest(
        self, observations: Iterable[FreightObservation], *, horizon_days: int
    ) -> dict[str, EvaluationMetrics]:
        if horizon_days not in SUPPORTED_HORIZONS:
            raise ValueError(f"horizon_days must be one of {SUPPORTED_HORIZONS}")
        history = sorted(observations, key=lambda item: item.observed_at)
        predictions: dict[str, list[tuple[float, float]]] = {name: [] for name in self._models}
        for cutoff in range(1, len(history)):
            target_time = history[cutoff - 1].observed_at + timedelta(days=horizon_days)
            target = next(
                (item for item in history[cutoff:] if item.observed_at >= target_time),
                None,
            )
            if target is None:
                continue
            actual = target.rate
            training = [
                item.rate
                for item in history[:cutoff]
                if item.observed_at <= history[cutoff - 1].observed_at
            ]
            for name in self._models:
                predictions[name].append((self._predict(training, name), actual))
        baseline = self._metrics(predictions["naive"])
        return {
            name: EvaluationMetrics(
                model=name,
                horizon_days=horizon_days,
                observations=len(pairs),
                mae=self._metrics(pairs)[0],
                rmse=self._metrics(pairs)[1],
                baseline_mae=baseline[0],
                improvement_over_naive=(baseline[0] - self._metrics(pairs)[0]) / baseline[0]
                if baseline[0]
                else 0,
                residual_count=len(pairs),
                coverage_p10_p90=self._coverage(pairs),
            )
            for name, pairs in predictions.items()
        }

    def calibration(
        self,
        observations: Iterable[FreightObservation],
        *,
        horizon_days: int,
        model: ForecastModel = "naive",
    ) -> dict[str, float | int | str | None]:
        """Report empirical coverage of residual-derived 80% intervals."""

        history = sorted(observations, key=lambda item: item.observed_at)
        residuals = self._residuals(history, horizon_days, model)
        if not residuals:
            return {"status": "insufficient_history", "observations": 0, "coverage_p10_p90": None}
        interval = self._residual_quantiles(
            residuals, self._volatility([item.rate for item in history]), horizon_days
        )
        covered = sum(
            interval[0.1] <= error <= interval[0.9] for error in residuals
        ) / len(residuals)
        return {
            "status": "calibrated" if len(residuals) >= 20 else "insufficient_history",
            "observations": len(residuals),
            "coverage_p10_p90": covered,
        }

    def _residuals(
        self, history: list[FreightObservation], horizon_days: int, model: str
    ) -> list[float]:
        return [
            actual - prediction
            for prediction, actual in self._backtest_pairs(history, horizon_days, model)
        ]

    def _backtest_pairs(
        self, history: list[FreightObservation], horizon_days: int, model: str
    ) -> list[tuple[float, float]]:
        pairs: list[tuple[float, float]] = []
        for cutoff in range(1, len(history)):
            target_time = history[cutoff - 1].observed_at + timedelta(days=horizon_days)
            target = next(
                (item for item in history[cutoff:] if item.observed_at >= target_time),
                None,
            )
            if target is not None:
                training = [item.rate for item in history[:cutoff]]
                pairs.append((self._predict(training, model), target.rate))
        return pairs

    def _residual_quantiles(
        self, residuals: list[float], volatility: float, horizon_days: int
    ) -> dict[float, float]:
        if not residuals:
            scale = volatility * math.sqrt(horizon_days / 7)
            return {
                0.1: -1.28 * scale,
                0.25: -0.67 * scale,
                0.5: 0,
                0.75: 0.67 * scale,
                0.9: 1.28 * scale,
            }
        ordered = sorted(residuals)
        return {level: self._quantile(ordered, level) for level in (0.1, 0.25, 0.5, 0.75, 0.9)}

    def _coverage(self, pairs: list[tuple[float, float]]) -> float | None:
        if not pairs:
            return None
        residuals = [actual - prediction for prediction, actual in pairs]
        quantiles = self._residual_quantiles(residuals, 0, 7)
        return sum(
            quantiles[0.1] <= residual <= quantiles[0.9] for residual in residuals
        ) / len(residuals)

    @staticmethod
    def _quantile(values: list[float], level: float) -> float:
        position = (len(values) - 1) * level
        lower = math.floor(position)
        upper = math.ceil(position)
        if lower == upper:
            return values[lower]
        return values[lower] + (values[upper] - values[lower]) * (position - lower)

    def _predict(self, values: list[float], model: str) -> float:
        if model == "naive":
            return values[-1]
        if model == "rolling_mean":
            window = values[-7:]
            return sum(window) / len(window)
        if model == "exponential_smoothing":
            estimate = values[0]
            for value in values[1:]:
                estimate = 0.3 * value + 0.7 * estimate
            return estimate
        raise ValueError(f"unsupported forecast model: {model}")

    @staticmethod
    def _metrics(pairs: list[tuple[float, float]]) -> tuple[float | None, float | None]:
        if not pairs:
            return None, None
        errors = [prediction - actual for prediction, actual in pairs]
        return sum(abs(error) for error in errors) / len(errors), math.sqrt(
            sum(error**2 for error in errors) / len(errors)
        )

    @staticmethod
    def _volatility(values: list[float]) -> float:
        mean = sum(values) / len(values)
        return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))

    _models = ("naive", "rolling_mean", "exponential_smoothing")


forecast_engine = ForecastEngine()

__all__ = [
    "EvaluationMetrics",
    "ForecastEngine",
    "ForecastModel",
    "ForecastResult",
    "FreightObservation",
    "CalibrationStatus",
    "SUPPORTED_HORIZONS",
    "forecast_engine",
]
