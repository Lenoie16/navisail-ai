"""Append-only audit event service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    actor: str
    action: str
    entity_type: str
    entity_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = Field(default_factory=dict)


class AuditService:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> AuditEvent:
        self._events.append(event)
        return event

    def for_entity(self, entity_type: str, entity_id: str) -> tuple[AuditEvent, ...]:
        return tuple(
            event
            for event in self._events
            if event.entity_type == entity_type and event.entity_id == entity_id
        )


audit_service = AuditService()
