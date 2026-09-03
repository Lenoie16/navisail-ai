"""Vessel CRUD repository."""

from app.models.all import Vessel
from app.repositories.base import Repository
from sqlalchemy.orm import Session


class VesselRepository(Repository[Vessel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Vessel)
