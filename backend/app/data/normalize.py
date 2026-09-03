"""Stable normalization utilities for source payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID


def normalize_payload(value: Any) -> Any:
    """Return a deterministic JSON-compatible representation.

    Keys are sorted and strings are trimmed. No provider-specific interpretation
    is performed here, so normalization is safe to repeat.
    """

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key).strip(): normalize_payload(value[key])
            for key in sorted(value, key=lambda item: str(item).strip())
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [normalize_payload(item) for item in value]
    if isinstance(value, str):
        return value.strip()
    return value


def normalize_record_payload(record: Any) -> Any:
    """Normalize the payload while preserving all envelope metadata."""

    if hasattr(record, "model_copy"):
        payload = normalize_payload(record.normalized_payload.model_dump(mode="python"))
        typed_payload = record.normalized_payload.__class__.model_validate(payload)
        return record.model_copy(update={"normalized_payload": typed_payload})
    raise TypeError("record must be a Pydantic source record")
