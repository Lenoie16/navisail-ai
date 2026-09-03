"""Plant CRUD repository."""

from app.models.all import Plant
from app.repositories.base import Repository
from sqlalchemy.orm import Session


class PlantRepository(Repository[Plant]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Plant)
