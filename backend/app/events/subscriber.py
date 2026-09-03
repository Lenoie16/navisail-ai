"""Subscriber helpers for domain event consumers."""

from collections.abc import AsyncIterator
from uuid import UUID

from app.events.bus import event_bus
from app.events.types import DomainEvent


def subscribe_events(
    *, decision_session_id: UUID | None = None, last_event_id: UUID | None = None
) -> AsyncIterator[DomainEvent]:
    return event_bus.subscribe(
        decision_session_id=decision_session_id,
        last_event_id=last_event_id,
    )
