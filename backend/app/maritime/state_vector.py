"""Canonical, versioned maritime state assembly and snapshot comparison."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid5

from app.data.contracts import SourceRecord
from app.data.freshness import FreshnessInfo, FreshnessState, evaluate_freshness
from pydantic import BaseModel, ConfigDict, Field

_NAMESPACE = UUID("b9c064e8-7bd8-4d4e-9f8f-b08d8e6d7c51")
STATE_COMPONENTS = (
    "shipment",
    "cargo",
    "origin_destination",
    "vessel",
    "ais",
    "port",
    "berth",
    "route",
    "freight",
    "congestion",
    "weather",
    "fuel",
    "fx",
    "inventory",
    "market",
    "risk",
)


class StateComponent(BaseModel):
    """One domain component with its source-of-truth metadata."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    source: str = Field(min_length=1)
    quality: float = Field(ge=0, le=1)
    freshness: FreshnessInfo
    status: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    data: Any

    @classmethod
    def from_source_record(
        cls, record: SourceRecord[Any], *, now: datetime | None = None
    ) -> StateComponent:
        current = (now or datetime.now(UTC)).astimezone(UTC)
        freshness = record.freshness
        if freshness.state is FreshnessState.UNKNOWN:
            freshness = evaluate_freshness(
                record.observed_at, now=current, domain=record.domain.value
            )
        return cls(
            timestamp=record.observed_at,
            source=record.source,
            quality=record.quality_score,
            freshness=freshness,
            status=record.status.value,
            confidence=record.quality_score,
            data=record.normalized_payload.model_dump(mode="json"),
        )


class MaritimeStateVector(BaseModel):
    """The only shared cross-domain state contract for downstream engines."""

    model_config = ConfigDict(extra="forbid")

    snapshot_id: UUID
    version: int = Field(ge=1)
    generated_at: datetime
    effective_at: datetime
    decision_session_id: UUID
    components: dict[str, StateComponent]


class StateDiff(BaseModel):
    """Material and non-material changes between two state snapshots."""

    from_snapshot_id: UUID
    to_snapshot_id: UUID
    added: list[str]
    removed: list[str]
    changed: list[str]
    stale: list[str]
    material_changes: list[str]


def build_state_vector(
    components: Mapping[str, StateComponent | Mapping[str, Any] | SourceRecord[Any]],
    *,
    decision_session_id: UUID,
    version: int = 1,
    effective_at: datetime | None = None,
    generated_at: datetime | None = None,
) -> MaritimeStateVector:
    """Build a reproducible snapshot from normalized component inputs."""

    generated = (generated_at or datetime.now(UTC)).astimezone(UTC)
    effective = (effective_at or generated).astimezone(UTC)
    normalized: dict[str, StateComponent] = {}
    for name in sorted(components):
        value = components[name]
        if isinstance(value, SourceRecord):
            normalized[name] = StateComponent.from_source_record(value, now=generated)
        else:
            normalized[name] = (
                value if isinstance(value, StateComponent) else StateComponent.model_validate(value)
            )
    payload = {
        "decision_session_id": str(decision_session_id),
        "version": version,
        "generated_at": generated.isoformat(),
        "effective_at": effective.isoformat(),
        "components": {
            name: component.model_dump(mode="json") for name, component in normalized.items()
        },
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return MaritimeStateVector(
        snapshot_id=uuid5(_NAMESPACE, digest),
        version=version,
        generated_at=generated,
        effective_at=effective,
        decision_session_id=decision_session_id,
        components=normalized,
    )


def diff_state_vectors(before: MaritimeStateVector, after: MaritimeStateVector) -> StateDiff:
    """Compare component payloads and metadata without hiding stale information."""

    before_names, after_names = set(before.components), set(after.components)
    added = sorted(after_names - before_names)
    removed = sorted(before_names - after_names)
    changed: list[str] = []
    stale: list[str] = []
    for name in sorted(after_names):
        if name not in before_names:
            if after.components[name].freshness.state is FreshnessState.STALE:
                stale.append(name)
            continue
        if before.components[name].model_dump(mode="json") != after.components[name].model_dump(
            mode="json"
        ):
            changed.append(name)
        if after.components[name].freshness.state is FreshnessState.STALE:
            stale.append(name)
    material = sorted(set(added + removed + changed))
    return StateDiff(
        from_snapshot_id=before.snapshot_id,
        to_snapshot_id=after.snapshot_id,
        added=added,
        removed=removed,
        changed=changed,
        stale=stale,
        material_changes=material,
    )


class SnapshotStore:
    """Process-local store until durable snapshot persistence is introduced."""

    def __init__(self) -> None:
        self._snapshots: dict[UUID, MaritimeStateVector] = {}

    def save(self, snapshot: MaritimeStateVector) -> MaritimeStateVector:
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get(self, snapshot_id: UUID) -> MaritimeStateVector | None:
        return self._snapshots.get(snapshot_id)

    def by_session(self, session_id: UUID) -> list[MaritimeStateVector]:
        return sorted(
            (item for item in self._snapshots.values() if item.decision_session_id == session_id),
            key=lambda item: (item.version, item.generated_at),
        )


snapshot_store = SnapshotStore()
