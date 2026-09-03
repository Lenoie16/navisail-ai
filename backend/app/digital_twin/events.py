"""Digital-twin event and transition records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

TwinEventType = Literal[
    "vessel departure",
    "vessel delay",
    "port arrival",
    "queue formation",
    "berth assignment",
    "loading/discharge",
    "departure",
    "inland arrival",
    "inventory consumption",
]


class TwinEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: TwinEventType
    occurred_at: datetime
    state_before: dict[str, Any]
    state_after: dict[str, Any]
    details: dict[str, Any] = Field(default_factory=dict)


__all__ = ["TwinEvent", "TwinEventType"]
