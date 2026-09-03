"""Plant CRUD endpoints."""

from app.api.routes.crud import crud_router
from app.schemas.plant import PlantCreate, PlantRead, PlantUpdate
from app.services.plant_service import PlantService

router = crud_router(
    path="plants",
    tag="plants",
    service=PlantService,
    create_schema=PlantCreate,
    update_schema=PlantUpdate,
    read_schema=PlantRead,
)
