"""Deterministic freshness evaluation for source records."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class FreshnessState(StrEnum):
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class FreshnessInfo(BaseModel):
    """The age and policy decision for an observation."""

    model_config = ConfigDict(extra="forbid")

    state: FreshnessState = FreshnessState.UNKNOWN
    age_seconds: float | None = Field(default=None, ge=0)
    threshold_seconds: int | None = Field(default=None, gt=0)
    evaluated_at: datetime | None = None


# Conservative defaults; providers can supply a more specific policy later.
DEFAULT_THRESHOLDS: dict[str, int] = {
    "ais_vessel": 15 * 60,
    "weather": 60 * 60,
    "freight_market": 24 * 60 * 60,
    "fuel": 24 * 60 * 60,
    "fx": 60 * 60,
    "port": 7 * 24 * 60 * 60,
    "berth": 24 * 60 * 60,
    "inventory": 24 * 60 * 60,
    "route_reference": 30 * 24 * 60 * 60,
    "news_geopolitical": 24 * 60 * 60,
}


def evaluate_freshness(
    observed_at: datetime,
    *,
    now: datetime | None = None,
    threshold_seconds: int | None = None,
    domain: str | None = None,
) -> FreshnessInfo:
    """Evaluate age using UTC and a deterministic, explicit threshold."""

    current = (now or datetime.now(UTC)).astimezone(UTC)
    observed = observed_at.astimezone(UTC)
    age = max(0.0, (current - observed).total_seconds())
    threshold = threshold_seconds or DEFAULT_THRESHOLDS.get(domain or "", 24 * 60 * 60)
    return FreshnessInfo(
        state=FreshnessState.FRESH if age <= threshold else FreshnessState.STALE,
        age_seconds=age,
        threshold_seconds=threshold,
        evaluated_at=current,
    )
