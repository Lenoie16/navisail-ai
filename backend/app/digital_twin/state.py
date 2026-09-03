"""Typed digital-twin state and what-if parameters."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TwinScenarioParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_date: datetime | None = None
    port_id: str | None = None
    vessel_id: str | None = None
    route_id: str | None = None
    contract: str | None = None
    disruption_assumptions: dict[str, float | int | str | bool] = Field(default_factory=dict)
    delay_hours: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def normalize_booking_date(self) -> TwinScenarioParameters:
        if self.booking_date is not None:
            if self.booking_date.tzinfo is None or self.booking_date.utcoffset() is None:
                raise ValueError("booking_date must include a timezone")
            self.booking_date = self.booking_date.astimezone(UTC)
        return self


class TwinState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: datetime
    shipment: dict[str, Any] = Field(default_factory=dict)
    vessels: tuple[dict[str, Any], ...] = ()
    ports: tuple[dict[str, Any], ...] = ()
    berths: tuple[dict[str, Any], ...] = ()
    routes: tuple[dict[str, Any], ...] = ()
    voyage_states: dict[str, str] = Field(default_factory=dict)
    inventory: dict[str, float] = Field(default_factory=dict)
    congestion: dict[str, Any] = Field(default_factory=dict)
    weather: dict[str, Any] = Field(default_factory=dict)
    market_conditions: dict[str, Any] = Field(default_factory=dict)
    selected_port_id: str | None = None
    selected_vessel_id: str | None = None
    selected_route_id: str | None = None
    selected_contract: str | None = None


__all__ = ["TwinScenarioParameters", "TwinState"]
