"""Shipment CRUD service."""

from app.models.all import Shipment
from app.repositories.shipment_repository import ShipmentRepository
from app.services.crud import CrudService
from sqlalchemy.orm import Session


class ShipmentService(CrudService[Shipment]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ShipmentRepository)
