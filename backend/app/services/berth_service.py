"""Berth CRUD service."""

from app.models.all import Berth
from app.repositories.berth_repository import BerthRepository
from app.services.crud import CrudService
from sqlalchemy.orm import Session


class BerthService(CrudService[Berth]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, BerthRepository)
