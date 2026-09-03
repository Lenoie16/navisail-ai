"""Deterministic port congestion and waiting-time intelligence."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any, Literal

from app.maritime.state_vector import MaritimeStateVector
from app.maritime.vessels.intelligence import AISObservation, normalize_ais
from pydantic import BaseModel, ConfigDict, Field, model_validator

CongestionScenario = Literal["normal", "moderate", "severe", "outage"]


class PortTimeWindow(BaseModel):
	model_config = ConfigDict(extra="forbid")

	port_id: str = Field(min_length=1)
	start: datetime
	end: datetime

	@model_validator(mode="after")
	def valid_window(self) -> PortTimeWindow:
		if self.start.tzinfo is None or self.end.tzinfo is None:
			raise ValueError("time window timestamps must include a timezone")
		if self.end < self.start:
			raise ValueError("window end must not precede window start")
		self.start = self.start.astimezone(UTC)
		self.end = self.end.astimezone(UTC)
		return self


class PortCongestionInput(BaseModel):
	model_config = ConfigDict(extra="forbid")

	window: PortTimeWindow
	ais_arrivals: list[AISObservation] = Field(default_factory=list)
	vessel_count: int = Field(default=0, ge=0)
	historical_throughput_vessels: float = Field(default=0, ge=0)
	berth_occupancy: float = Field(default=0, ge=0, le=1)
	queue_vessels: float = Field(default=0, ge=0)
	weather_factor: float = Field(default=0, ge=0, le=1)
	operational_status: str = "operational"
	historical_waiting_hours: list[float] = Field(default_factory=list, min_length=0)
	scenario: CongestionScenario = "normal"


class PortImpact(BaseModel):
	eta_delay_hours: float = Field(ge=0)
	discharge_delay_hours: float = Field(ge=0)
	landed_cost_delta: float = Field(ge=0)
	stockout_risk_delta: float = Field(ge=0, le=1)
	recommendation: str


class CongestionPrediction(BaseModel):
	port_id: str
	window_start: datetime
	window_end: datetime
	congestion_score: float = Field(ge=0, le=1)
	expected_waiting_hours: float = Field(ge=0)
	p50_waiting_hours: float = Field(ge=0)
	p75_waiting_hours: float = Field(ge=0)
	p90_waiting_hours: float = Field(ge=0)
	congestion_trend: Literal["stable", "increasing", "decreasing"]
	confidence: float = Field(ge=0, le=1)
	key_drivers: tuple[str, ...]
	scenario: CongestionScenario
	impact: PortImpact


class CongestionEngine:
	"""Estimate congestion as a read-only projection of operational inputs."""

	def predict(self, inputs: PortCongestionInput) -> CongestionPrediction:
		scenario_multiplier = {
			"normal": 1.0,
			"moderate": 1.35,
			"severe": 2.25,
			"outage": 4.0,
		}[inputs.scenario]
		arrivals = max(inputs.vessel_count, len(inputs.ais_arrivals))
		arrival_pressure = min(1.0, arrivals / max(inputs.historical_throughput_vessels, 1))
		occupancy_pressure = inputs.berth_occupancy
		queue_pressure = min(1.0, inputs.queue_vessels / max(arrivals, 1))
		raw_score = (
			0.35 * arrival_pressure
			+ 0.3 * occupancy_pressure
			+ 0.2 * queue_pressure
			+ 0.15 * inputs.weather_factor
		)
		if inputs.operational_status.lower() not in {"operational", "normal"}:
			raw_score += 0.25
		score = min(1.0, raw_score * scenario_multiplier)
		historical_wait = self._median(inputs.historical_waiting_hours)
		baseline_wait = historical_wait or 4.0
		expected_wait = baseline_wait * (1 + 2 * score) * scenario_multiplier
		if inputs.scenario == "outage" or inputs.operational_status.lower() == "outage":
			expected_wait = max(expected_wait, baseline_wait * 4)
		p50 = expected_wait
		p75 = expected_wait * (1.25 + score * 0.25)
		p90 = expected_wait * (1.55 + score * 0.45)
		drivers = self._drivers(inputs, arrival_pressure, occupancy_pressure, queue_pressure)
		trend = "increasing" if score >= 0.7 else "decreasing" if score <= 0.25 else "stable"
		confidence = min(
			0.95,
			0.45
			+ min(0.35, len(inputs.historical_waiting_hours) / 40)
			+ (0.1 if inputs.ais_arrivals else 0),
		)
		impact = PortImpact(
			eta_delay_hours=expected_wait,
			discharge_delay_hours=expected_wait * 0.75,
			landed_cost_delta=expected_wait * 100,
			stockout_risk_delta=min(1.0, expected_wait / 240),
			recommendation=(
				"avoid or re-time port call" if score >= 0.7 else "monitor port conditions"
			),
		)
		return CongestionPrediction(
			port_id=inputs.window.port_id,
			window_start=inputs.window.start,
			window_end=inputs.window.end,
			congestion_score=score,
			expected_waiting_hours=expected_wait,
			p50_waiting_hours=p50,
			p75_waiting_hours=p75,
			p90_waiting_hours=p90,
			congestion_trend=trend,
			confidence=confidence,
			key_drivers=tuple(drivers),
			scenario=inputs.scenario,
			impact=impact,
		)

	def predict_many(self, inputs: Iterable[PortCongestionInput]) -> list[CongestionPrediction]:
		return [self.predict(item) for item in inputs]

	def from_state_vector(
		self, state: MaritimeStateVector, window: PortTimeWindow, **kwargs: Any
	) -> CongestionPrediction:
		"""Project state-vector data without changing or saving the state."""

		ais_component = state.components.get("ais")
		arrivals = []
		if ais_component is not None:
			values = (
				ais_component.data
				if isinstance(ais_component.data, list)
				else [ais_component.data]
			)
			arrivals = [
				normalize_ais(
					{
						**value,
						"observed_at": value.get("observed_at", ais_component.timestamp),
					},
					source=ais_component.source,
				)
				for value in values
			]
		return self.predict(PortCongestionInput(window=window, ais_arrivals=arrivals, **kwargs))

	@staticmethod
	def _median(values: list[float]) -> float | None:
		if not values:
			return None
		ordered = sorted(values)
		midpoint = len(ordered) // 2
		return (
			ordered[midpoint]
			if len(ordered) % 2
			else (ordered[midpoint - 1] + ordered[midpoint]) / 2
		)

	@staticmethod
	def _drivers(
		inputs: PortCongestionInput,
		arrival_pressure: float,
		occupancy_pressure: float,
		queue_pressure: float,
	) -> list[str]:
		drivers: list[tuple[float, str]] = [
			(arrival_pressure, "AIS arrivals and vessel count"),
			(occupancy_pressure, "berth occupancy"),
			(queue_pressure, "queue approximation"),
			(inputs.weather_factor, "weather conditions"),
		]
		if inputs.operational_status.lower() not in {"operational", "normal"}:
			drivers.append((1.0, "operational status"))
		if inputs.scenario != "normal":
			drivers.append((1.0, f"scenario: {inputs.scenario}"))
		return [name for _, name in sorted(drivers, reverse=True) if _ > 0]


congestion_engine = CongestionEngine()

__all__ = [
	"CongestionEngine",
	"CongestionPrediction",
	"CongestionScenario",
	"PortCongestionInput",
	"PortImpact",
	"PortTimeWindow",
	"congestion_engine",
]
