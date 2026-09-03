"""Read-only data source health endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.data.pipeline import registry

router = APIRouter(tags=["data-health"])


class SourceHealth(BaseModel):
    source: str
    latest_update: datetime
    latest_observed_at: datetime
    status: str
    quality: float
    quality_score: float
    freshness: dict[str, Any]
    records: int


class DataHealth(BaseModel):
    sources: list[SourceHealth]
    quarantined_records: int


@router.get("/data-health", response_model=DataHealth)
async def data_health() -> DataHealth:
    """Return the latest accepted record health per source."""

    return DataHealth(
        sources=[SourceHealth.model_validate(item) for item in registry.health()],
        quarantined_records=len(registry.quarantine),
    )


@router.get("/data-health/sources", response_model=list[SourceHealth])
async def data_health_sources() -> list[SourceHealth]:
    """Return source health rows for dashboards and operators."""

    return [SourceHealth.model_validate(item) for item in registry.health()]
