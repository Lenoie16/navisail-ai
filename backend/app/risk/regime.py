"""Freight market regime and abnormal-shock detection."""

from __future__ import annotations

import math
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

Regime = Literal["stable", "rising", "falling", "volatile", "disrupted", "shock/recovery"]
ShockType = Literal[
    "freight spike", "port outage", "congestion shock", "supply reduction", "fuel shock"
]


class MarketSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observed_at: datetime
    freight_rate: float = Field(gt=0)
    volume: float = Field(default=0, ge=0)
    congestion_score: float = Field(default=0, ge=0, le=1)
    vessel_availability: float = Field(default=1, ge=0, le=1)
    fuel_price: float = Field(default=0, ge=0)
    operational_status: str = "operational"
    external_signal: float = 0

    @model_validator(mode="after")
    def timezone_required(self) -> MarketSignal:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must include a timezone")
        self.observed_at = self.observed_at.astimezone(UTC)
        return self


class ShockEvent(BaseModel):
    shock_type: ShockType
    detected_at: datetime
    severity: float = Field(ge=0, le=1)
    change: float
    evidence: tuple[str, ...]


class MarketRegimeState(BaseModel):
    regime: Regime
    confidence: float = Field(ge=0, le=1)
    drivers: tuple[str, ...]
    severity: float = Field(ge=0, le=1)
    detected_at: datetime
    source_state_snapshot: UUID | None
    shocks: tuple[ShockEvent, ...]
    forecast_market_condition: Literal["stable", "volatile", "rising", "falling"]
    risk_scenario_hint: Literal["normal", "volatile", "severe"]


class MarketRegimeDetector:
    """Classify market behavior from ordered historical signals."""

    def detect(
        self,
        signals: Iterable[MarketSignal],
        *,
        source_state_snapshot: UUID | None = None,
    ) -> MarketRegimeState:
        history = sorted(signals, key=lambda signal: signal.observed_at)
        if not history:
            raise ValueError("at least one market signal is required")
        changes = [
            (current.freight_rate - previous.freight_rate) / previous.freight_rate
            for previous, current in zip(history[:-1], history[1:], strict=True)
        ]
        latest = history[-1]
        average_change = sum(changes) / len(changes) if changes else 0
        volatility = self._volatility(changes)
        shocks = self._shocks(history, changes)
        drivers: list[str] = []
        if average_change > 0.03:
            drivers.append("freight rates rising")
        elif average_change < -0.03:
            drivers.append("freight rates falling")
        if volatility > 0.08:
            drivers.append("freight changes are volatile")
        if latest.congestion_score >= 0.75:
            drivers.append("high congestion")
        if latest.vessel_availability <= 0.35:
            drivers.append("low vessel availability")
        if latest.operational_status.lower() in {"outage", "closed", "disrupted"}:
            drivers.append("port operational disruption")
        if (
            latest.fuel_price
            and len(history) > 1
            and latest.fuel_price > history[-2].fuel_price * 1.15
        ):
            drivers.append("fuel prices increased sharply")
        regime = self._classify(history, average_change, volatility, shocks)
        severity = min(1.0, max([shock.severity for shock in shocks], default=volatility * 4))
        confidence = min(0.95, 0.45 + min(0.35, len(history) / 30) + (0.1 if shocks else 0))
        forecast_condition = (
            "volatile" if regime in {"volatile", "disrupted", "shock/recovery"} else regime
        )
        risk_hint = "severe" if severity >= 0.7 else "volatile" if severity >= 0.3 else "normal"
        return MarketRegimeState(
            regime=regime,
            confidence=confidence,
            drivers=tuple(drivers) or ("insufficient directional evidence",),
            severity=severity,
            detected_at=latest.observed_at,
            source_state_snapshot=source_state_snapshot,
            shocks=tuple(shocks),
            forecast_market_condition=forecast_condition,
            risk_scenario_hint=risk_hint,
        )

    @staticmethod
    def _classify(
        history: list[MarketSignal],
        average_change: float,
        volatility: float,
        shocks: list[ShockEvent],
    ) -> Regime:
        latest = history[-1]
        if shocks and len(history) >= 2 and history[-2].freight_rate > latest.freight_rate:
            return "shock/recovery"
        if (
            latest.operational_status.lower() in {"outage", "closed", "disrupted"}
            or latest.vessel_availability <= 0.2
        ):
            return "disrupted"
        if volatility > 0.08:
            return "volatile"
        if average_change > 0.03:
            return "rising"
        if average_change < -0.03:
            return "falling"
        return "stable"

    @staticmethod
    def _shocks(history: list[MarketSignal], changes: list[float]) -> list[ShockEvent]:
        shocks: list[ShockEvent] = []
        for index, change in enumerate(changes, start=1):
            current = history[index]
            previous = history[index - 1]
            if change >= 0.2:
                shocks.append(
                    ShockEvent(
                        shock_type="freight spike",
                        detected_at=current.observed_at,
                        severity=min(1, change),
                        change=change,
                        evidence=(f"freight changed {change:.1%}",),
                    )
                )
            if current.congestion_score - previous.congestion_score >= 0.3:
                shocks.append(
                    ShockEvent(
                        shock_type="congestion shock",
                        detected_at=current.observed_at,
                        severity=current.congestion_score,
                        change=current.congestion_score - previous.congestion_score,
                        evidence=(f"congestion score reached {current.congestion_score:.2f}",),
                    )
                )
            if (
                current.fuel_price
                and previous.fuel_price
                and current.fuel_price >= previous.fuel_price * 1.2
            ):
                shocks.append(
                    ShockEvent(
                        shock_type="fuel shock",
                        detected_at=current.observed_at,
                        severity=min(1, current.fuel_price / previous.fuel_price - 1),
                        change=current.fuel_price / previous.fuel_price - 1,
                        evidence=(
                            "fuel price changed "
                            f"{current.fuel_price / previous.fuel_price - 1:.1%}",
                        ),
                    )
                )
            if current.vessel_availability <= 0.35 < previous.vessel_availability:
                shocks.append(
                    ShockEvent(
                        shock_type="supply reduction",
                        detected_at=current.observed_at,
                        severity=1 - current.vessel_availability,
                        change=current.vessel_availability - previous.vessel_availability,
                        evidence=(f"availability fell to {current.vessel_availability:.2f}",),
                    )
                )
            if current.operational_status.lower() in {"outage", "closed", "disrupted"}:
                shocks.append(
                    ShockEvent(
                        shock_type="port outage",
                        detected_at=current.observed_at,
                        severity=1,
                        change=1,
                        evidence=(f"status: {current.operational_status}",),
                    )
                )
        return shocks

    @staticmethod
    def _volatility(values: list[float]) -> float:
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


market_regime_detector = MarketRegimeDetector()

__all__ = [
    "MarketRegimeDetector",
    "MarketRegimeState",
    "MarketSignal",
    "ShockEvent",
    "market_regime_detector",
]
