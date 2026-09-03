"""Typed domain events shared by publishers and realtime consumers."""

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

EventType = Literal[
    "orchestration.started",
    "orchestration.completed",
    "forecast.started",
    "forecast.completed",
    "optimization.started",
    "optimization.completed",
    "recommendation.updated",
    "scenario.started",
    "scenario.completed",
    "approval.changed",
    "execution.changed",
    "maritime.state.updated",
    "datadocked.connected",
    "datadocked.disconnected",
    "datadocked.auth_failed",
    "datadocked.rate_limited",
    "datadocked.fetch_started",
    "datadocked.fetch_completed",
    "datadocked.fetch_failed",
    "external.maritime.data.updated",
]


class DomainEvent(BaseModel):
    """A stable, session-scoped event envelope suitable for SSE transport."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: UUID = Field(default_factory=uuid4)
    decision_session_id: UUID | None = None
    aggregate_id: str | None = None
    sequence: int = Field(ge=1)
    payload: dict[str, Any] = Field(default_factory=dict)

    def sse_data(self) -> str:
        return self.model_dump_json()
