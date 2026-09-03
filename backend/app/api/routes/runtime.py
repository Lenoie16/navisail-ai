"""Runtime data policy endpoint."""

from fastapi import APIRouter

from app.data.runtime import RuntimeDataStatus, runtime_data_status

router = APIRouter(tags=["runtime"])


@router.get("/runtime/data-status", response_model=RuntimeDataStatus)
async def data_status() -> RuntimeDataStatus:
    """Expose effective mode and fallback policy to operator-facing clients."""

    return await runtime_data_status()
