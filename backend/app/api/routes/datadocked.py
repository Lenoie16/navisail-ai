"""NAVISAIL-owned Data Docked diagnostics and normalized observation APIs."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.data.datadocked import DataDockedError, datadocked_provider, map_vessel_location
from app.data.pipeline import registry

router = APIRouter(prefix="/data-sources/datadocked", tags=["data-sources"])


class VesselLookupRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=32)


@router.get("/health")
async def health() -> dict[str, object]:
    return await datadocked_provider.health()


@router.post("/vessels/location")
async def vessel_location(request: VesselLookupRequest) -> dict[str, object]:
    try:
        payload = await datadocked_provider.get_vessel_location(request.identifier)
        record = map_vessel_location(payload)
        accepted, issues = registry.register(record)
        if not accepted:
            raise HTTPException(status_code=422, detail=[issue.model_dump() for issue in issues])
        return {
            "observation": record.model_dump(mode="json"),
            "source": record.source,
            "status": record.status,
            "freshness": record.freshness.model_dump(mode="json"),
        }
    except DataDockedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
