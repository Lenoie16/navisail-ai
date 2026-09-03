"""Port CRUD repository."""

from app.models.all import Port
from app.repositories.base import Repository
from sqlalchemy.orm import Session


class PortRepository(Repository[Port]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Port)
