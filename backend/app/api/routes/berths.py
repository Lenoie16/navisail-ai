"""Berth CRUD endpoints."""

from app.api.routes.crud import crud_router
from app.schemas.berth import BerthCreate, BerthRead, BerthUpdate
from app.services.berth_service import BerthService

router = crud_router(
    path="berths",
    tag="berths",
    service=BerthService,
    create_schema=BerthCreate,
    update_schema=BerthUpdate,
    read_schema=BerthRead,
)
