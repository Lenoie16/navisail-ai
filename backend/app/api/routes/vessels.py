"""Vessel CRUD endpoints."""

from app.api.routes.crud import crud_router
from app.schemas.vessel import VesselCreate, VesselRead, VesselUpdate
from app.services.vessel_service import VesselService

router = crud_router(
    path="vessels",
    tag="vessels",
    service=VesselService,
    create_schema=VesselCreate,
    update_schema=VesselUpdate,
    read_schema=VesselRead,
)
