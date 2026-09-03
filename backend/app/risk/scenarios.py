"""Scenario definitions for reproducible maritime risk simulation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RiskScenario(BaseModel):
	model_config = ConfigDict(extra="forbid")

	name: str = Field(min_length=1)
	freight_volatility: float = Field(default=0.1, ge=0)
	fuel_volatility: float = Field(default=0.1, ge=0)
	congestion_probability: float = Field(default=0.1, ge=0, le=1)
	waiting_hours: float = Field(default=4, ge=0)
	weather_probability: float = Field(default=0.1, ge=0, le=1)
	vessel_failure_probability: float = Field(default=0.02, ge=0, le=1)
	port_outage_probability: float = Field(default=0.01, ge=0, le=1)
	fx_volatility: float = Field(default=0.05, ge=0)
	operational_delay_hours: float = Field(default=2, ge=0)
	disruption_cost: float = Field(default=0, ge=0)


ScenarioName = Literal["normal", "volatile", "severe"]


DEFAULT_SCENARIOS: dict[ScenarioName, RiskScenario] = {
	"normal": RiskScenario(name="normal"),
	"volatile": RiskScenario(
		name="volatile",
		freight_volatility=0.2,
		fuel_volatility=0.2,
		congestion_probability=0.25,
		waiting_hours=12,
		weather_probability=0.2,
		fx_volatility=0.1,
		operational_delay_hours=8,
	),
	"severe": RiskScenario(
		name="severe",
		freight_volatility=0.3,
		fuel_volatility=0.3,
		congestion_probability=0.5,
		waiting_hours=36,
		weather_probability=0.4,
		vessel_failure_probability=0.1,
		port_outage_probability=0.08,
		fx_volatility=0.15,
		operational_delay_hours=24,
		disruption_cost=100_000,
	),
}

__all__ = ["DEFAULT_SCENARIOS", "RiskScenario", "ScenarioName"]
