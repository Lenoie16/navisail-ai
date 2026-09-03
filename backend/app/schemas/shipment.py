"""Shipment API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.models.all import ShipmentStatus
from app.schemas.common import ORMModel
from pydantic import Field


class ShipmentCreate(ORMModel):
    reference: str = Field(min_length=1, max_length=80)
    commodity_id: UUID | None = None
    plant_id: UUID | None = None
    origin_id: UUID | None = None
    origin_port_id: UUID | None = None
    destination_port_id: UUID | None = None
    quantity_tonnes: Decimal = Field(gt=0)
    status: ShipmentStatus = ShipmentStatus.planned
    planned_departure_at: datetime | None = None
    planned_arrival_at: datetime | None = None


class ShipmentUpdate(ORMModel):
    reference: str | None = Field(default=None, min_length=1, max_length=80)
    commodity_id: UUID | None = None
    plant_id: UUID | None = None
    origin_id: UUID | None = None
    origin_port_id: UUID | None = None
    destination_port_id: UUID | None = None
    quantity_tonnes: Decimal | None = Field(default=None, gt=0)
    status: ShipmentStatus | None = None
    planned_departure_at: datetime | None = None
    planned_arrival_at: datetime | None = None


class ShipmentRead(ShipmentCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
