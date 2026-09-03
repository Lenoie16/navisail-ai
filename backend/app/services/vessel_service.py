"""Vessel CRUD service."""

from app.models.all import Vessel
from app.repositories.vessel_repository import VesselRepository
from app.services.crud import CrudService
from sqlalchemy.orm import Session


class VesselService(CrudService[Vessel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, VesselRepository)
