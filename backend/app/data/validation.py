"""Reusable validation and quarantine decisions for source records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from app.data.contracts import SourceRecord
from app.data.freshness import FreshnessState, evaluate_freshness

_UNIT_ALIASES = {
    "mt": "tonnes",
    "metric_ton": "tonnes",
    "metric_tonne": "tonnes",
    "metric_tonnes": "tonnes",
    "tonne": "tonnes",
    "l": "litres",
    "liter": "litres",
    "liters": "litres",
    "km": "kilometres",
    "kilometer": "kilometres",
    "kilometers": "kilometres",
}
_KNOWN_UNITS = {
    "tonnes",
    "kg",
    "litres",
    "m3",
    "gallons",
    "nm",
    "kilometres",
    "knots",
    "usd/tonne",
    "usd/mt",
    "usd/day",
    "usd/m3",
    "usd/litre",
    "units",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    field: str | None = None


def validate_record(
    record: SourceRecord[Any],
    *,
    now: datetime | None = None,
    max_future_seconds: int = 300,
    stale_after_seconds: int | None = None,
) -> tuple[ValidationIssue, ...]:
    """Apply cross-domain checks not expressible in a payload model."""

    current = (now or datetime.now(UTC)).astimezone(UTC)
    issues: list[ValidationIssue] = []
    if record.observed_at > current:
        age = (record.observed_at - current).total_seconds()
        if age > max_future_seconds:
            issues.append(
                ValidationIssue(
                    "future_timestamp", "observed_at is too far in the future", "observed_at"
                )
            )
    if (
        record.ingested_at > current
        and (record.ingested_at - current).total_seconds() > max_future_seconds
    ):
        issues.append(
            ValidationIssue(
                "future_timestamp", "ingested_at is too far in the future", "ingested_at"
            )
        )
    if record.quality_score < 0 or record.quality_score > 1:
        issues.append(ValidationIssue("quality_range", "quality_score must be between 0 and 1"))
    if stale_after_seconds is not None:
        freshness = evaluate_freshness(
            record.observed_at,
            now=current,
            threshold_seconds=stale_after_seconds,
            domain=record.domain.value,
        )
        if freshness.state is FreshnessState.STALE:
            issues.append(
                ValidationIssue(
                    "stale_data",
                    f"observation is older than {stale_after_seconds} seconds",
                    "observed_at",
                )
            )
    payload = record.normalized_payload.model_dump()
    for key, value in _walk(payload):
        key_lower = key.lower()
        if value is None and key_lower in {"source", "source_identifier", "unit"}:
            issues.append(ValidationIssue("missing_value", f"{key} is required", key))
        if (
            isinstance(value, (int, float))
            and value < 0
            and any(token in key_lower for token in ("quantity", "volume", "amount"))
        ):
            issues.append(ValidationIssue("negative_quantity", f"{key} cannot be negative", key))
        if key_lower in {"latitude", "lat"} and not -90 <= value <= 90:
            issues.append(ValidationIssue("coordinate_range", f"{key} is outside [-90, 90]", key))
        if key_lower in {"longitude", "lon", "lng"} and not -180 <= value <= 180:
            issues.append(ValidationIssue("coordinate_range", f"{key} is outside [-180, 180]", key))
    units = [
        value.strip().lower()
        for key, value in _walk(payload)
        if "unit" in key.lower() and isinstance(value, str)
    ]
    if payload.get("unit") is not None and not isinstance(payload["unit"], str):
        issues.append(ValidationIssue("inconsistent_unit", "unit must be a string", "unit"))
    unknown_units = [unit for unit in units if unit not in _KNOWN_UNITS]
    issues.extend(
        ValidationIssue("inconsistent_unit", f"unsupported unit: {unit}", "unit")
        for unit in unknown_units
    )
    canonical_units = {_UNIT_ALIASES.get(unit, unit) for unit in units}
    if len(canonical_units) > 1:
        issues.append(
            ValidationIssue("inconsistent_unit", "payload contains conflicting units", "unit")
        )
    return tuple(issues)


def validate_payload_model(model_type: type[Any], payload: Any) -> tuple[ValidationIssue, ...]:
    """Validate untrusted payloads without leaking Pydantic exceptions."""

    try:
        model_type.model_validate(payload)
    except ValidationError as exc:
        return tuple(
            ValidationIssue("invalid_payload", error["msg"], ".".join(str(x) for x in error["loc"]))
            for error in exc.errors()
        )
    return ()


def _walk(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            items.append((str(key), child))
            items.extend(_walk(child, name))
    elif isinstance(value, list):
        for child in value:
            items.extend(_walk(child, prefix))
    return items
