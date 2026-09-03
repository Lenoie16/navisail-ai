"""Port CRUD service."""

from app.models.all import Port
from app.repositories.port_repository import PortRepository
from app.services.crud import CrudService
from sqlalchemy.orm import Session


class PortService(CrudService[Port]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PortRepository)
