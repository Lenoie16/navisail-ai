"""Plant CRUD service."""

from app.models.all import Plant
from app.repositories.plant_repository import PlantRepository
from app.services.crud import CrudService
from sqlalchemy.orm import Session


class PlantService(CrudService[Plant]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PlantRepository)
