"""Berth CRUD repository."""

from app.models.all import Berth
from app.repositories.base import Repository
from sqlalchemy.orm import Session


class BerthRepository(Repository[Berth]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Berth)
