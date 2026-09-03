"""Convenience publisher preserving correlation and session context."""

from uuid import UUID
from typing import Any

from app.events.bus import event_bus
from app.events.types import DomainEvent, EventType


async def publish_event(
    event_type: EventType,
    *,
    payload: dict[str, Any] | None = None,
    decision_session_id: UUID | None = None,
    aggregate_id: str | None = None,
    correlation_id: UUID | None = None,
) -> DomainEvent:
    values: dict[str, Any] = {
        "event_type": event_type,
        "payload": payload or {},
        "decision_session_id": decision_session_id,
        "aggregate_id": aggregate_id,
        "sequence": 1,
    }
    if correlation_id is not None:
        values["correlation_id"] = correlation_id
    return await event_bus.publish(DomainEvent(**values))
