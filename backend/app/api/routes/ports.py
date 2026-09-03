"""Port CRUD endpoints."""

from app.api.routes.crud import crud_router
from app.schemas.port import PortCreate, PortRead, PortUpdate
from app.services.port_service import PortService

router = crud_router(
    path="ports",
    tag="ports",
    service=PortService,
    create_schema=PortCreate,
    update_schema=PortUpdate,
    read_schema=PortRead,
)
