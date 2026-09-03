"""Shipment CRUD endpoints."""

from app.api.routes.crud import crud_router
from app.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from app.services.shipment_service import ShipmentService

router = crud_router(
    path="shipments",
    tag="shipments",
    service=ShipmentService,
    create_schema=ShipmentCreate,
    update_schema=ShipmentUpdate,
    read_schema=ShipmentRead,
)
