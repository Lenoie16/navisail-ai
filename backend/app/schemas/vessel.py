"""Vessel API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.models.all import VesselStatus
from app.schemas.common import ORMModel
from pydantic import Field


class VesselCreate(ORMModel):
    name: str = Field(min_length=1, max_length=160)
    imo_number: str = Field(pattern=r"^\d{7}$")
    vessel_type: str = Field(min_length=1, max_length=80)
    operator: str | None = None
    deadweight_tonnes: Decimal | None = Field(default=None, gt=0)
    loa_m: Decimal | None = Field(default=None, gt=0)
    beam_m: Decimal | None = Field(default=None, gt=0)
    max_draft_m: Decimal | None = Field(default=None, gt=0)
    speed_knots: Decimal | None = Field(default=None, gt=0)
    fuel_characteristics: dict[str, object] | None = None
    status: VesselStatus = VesselStatus.active


class VesselUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    imo_number: str | None = Field(default=None, pattern=r"^\d{7}$")
    vessel_type: str | None = Field(default=None, min_length=1, max_length=80)
    operator: str | None = None
    deadweight_tonnes: Decimal | None = Field(default=None, gt=0)
    loa_m: Decimal | None = Field(default=None, gt=0)
    beam_m: Decimal | None = Field(default=None, gt=0)
    max_draft_m: Decimal | None = Field(default=None, gt=0)
    speed_knots: Decimal | None = Field(default=None, gt=0)
    fuel_characteristics: dict[str, object] | None = None
    status: VesselStatus | None = None


class VesselRead(VesselCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
