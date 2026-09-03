"""Typed records used by the deterministic synthetic data engine.

These models deliberately carry source status on every record.  Synthetic and demo
fixtures can therefore never be mistaken for a live provider feed.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.data.contracts import SourceStatus


class ShockType(StrEnum):
    """Supported deterministic operational and market shocks."""

    PORT_OUTAGE = "port_outage"
    CONGESTION_PLUS_5_DAYS = "congestion_plus_5_days"
    FREIGHT_SPIKE = "freight_spike"
    CYCLONE = "cyclone"
    FUEL_SPIKE = "fuel_spike"
    VESSEL_FAILURE = "vessel_failure"
    SEVERE_CONGESTION = "severe_congestion"


class SyntheticRecord(BaseModel):
    """Envelope for synthetic domains without a Phase 3 payload contract yet."""

    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_status: SourceStatus
    scenario_id: str = Field(min_length=1)
    observed_at: datetime
    geography: str = Field(min_length=1)
    payload: dict[str, Any]

    @property
    def status(self) -> SourceStatus:
        """Match the Phase 3 envelope naming used by typed records."""

        return self.source_status

    def __getitem__(self, key: str) -> Any:
        """Allow fixture consumers to use records like JSON objects."""

        if key == "status":
            return self.source_status
        return self.model_dump(mode="python")[key]

    def model_dump_jsonable(self) -> dict[str, Any]:
        """Return a JSON-compatible representation for deterministic artifacts."""

        serialized = self.model_dump(mode="json")
        serialized["status"] = serialized["source_status"]
        return serialized


class ShockDefinition(BaseModel):
    """A named shock and its deterministic effect parameters."""

    model_config = ConfigDict(extra="forbid")

    shock_id: str = Field(min_length=1)
    shock_type: ShockType
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    target: str = Field(min_length=1)
    parameters: dict[str, float | int | str]


__all__ = ["ShockDefinition", "ShockType", "SyntheticRecord"]
