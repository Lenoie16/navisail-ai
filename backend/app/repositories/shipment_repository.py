"""Shipment CRUD repository."""

from app.models.all import Shipment
from app.repositories.base import Repository
from sqlalchemy.orm import Session


class ShipmentRepository(Repository[Shipment]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Shipment)
