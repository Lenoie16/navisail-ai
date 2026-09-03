"""Transparent landed-cost contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CostComponentInput(BaseModel):
	model_config = ConfigDict(extra="forbid")

	component: str = Field(min_length=1)
	rate: float = Field(ge=0)
	currency: str = Field(min_length=3, max_length=3)
	unit: Literal["total", "per_tonne", "per_kg", "per_hour", "per_day"] = "total"
	quantity: float = Field(default=1, ge=0)
	source: str = Field(min_length=1)
	assumptions: tuple[str, ...] = ()
	risk_multiplier: float = Field(default=1, ge=1)


class FXQuote(BaseModel):
	model_config = ConfigDict(extra="forbid")

	base_currency: str = Field(min_length=3, max_length=3)
	quote_currency: str = Field(min_length=3, max_length=3)
	rate: float = Field(gt=0)
	timestamp: datetime
	source: str = Field(min_length=1)
	source_status: str = Field(min_length=1)

	@model_validator(mode="after")
	def different_currencies(self) -> FXQuote:
		if self.base_currency.upper() == self.quote_currency.upper():
			raise ValueError("FX quote currencies must differ")
		if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
			raise ValueError("FX timestamp must include a timezone")
		return self


class ScenarioAdjustment(BaseModel):
	model_config = ConfigDict(extra="forbid")

	name: str = "base"
	risk_multiplier: float = Field(default=1, ge=1)
	delay_hours: float = Field(default=0, ge=0)
	delay_cost_per_hour: float = Field(default=0, ge=0)
	disruption_cost: float = Field(default=0, ge=0)
	inventory_days: float = Field(default=0, ge=0)
	inventory_cost_per_tonne_day: float = Field(default=0, ge=0)


class CostComponent(BaseModel):
	component: str
	formula: str
	value: float = Field(ge=0)
	currency: str
	source: str
	assumptions: tuple[str, ...]


class LandedCostResult(BaseModel):
	components: tuple[CostComponent, ...]
	expected_landed_cost: float = Field(ge=0)
	risk_adjusted_landed_cost: float = Field(ge=0)
	cost_per_tonne: float = Field(ge=0)
	total_voyage_cost: float = Field(ge=0)
	currency: str
	quantity_tonnes: float = Field(gt=0)
	fx_timestamp: datetime | None
	fx_source: str | None
	fx_source_status: str | None
	scenario: str


__all__ = [
	"CostComponent",
	"CostComponentInput",
	"FXQuote",
	"LandedCostResult",
	"ScenarioAdjustment",
]
