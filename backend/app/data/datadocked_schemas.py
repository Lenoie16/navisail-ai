"""Tolerant provider response models with strict canonical output downstream."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VesselLocationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    imo: str | None = None
    mmsi: str | None = None
    vessel_name: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed: float | None = Field(default=None, ge=0)
    course: float | None = Field(default=None, ge=0, lt=360)
    heading: float | None = Field(default=None, ge=0, lt=360)
    draught: float | None = Field(default=None, ge=0)
    navigation_status: str | None = None
    destination: str | None = None
    eta: datetime | None = None
    last_port: str | None = None
    observed_at: datetime
    provider_source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
