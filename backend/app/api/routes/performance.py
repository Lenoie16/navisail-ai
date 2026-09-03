"""Performance diagnostics for local operation and tests."""

from fastapi import APIRouter

from app.core.performance import metrics_store

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/metrics")
async def get_metrics() -> dict[str, dict[str, float | int]]:
    return metrics_store.snapshot()
