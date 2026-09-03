"""Helpers for auditable state transitions."""

from typing import Any

from app.audit.service import AuditEvent, audit_service


def record_transition(
    *,
    actor: str,
    entity_type: str,
    entity_id: str,
    action: str,
    details: dict[str, Any],
) -> AuditEvent:
    return audit_service.record(
        AuditEvent(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
    )
