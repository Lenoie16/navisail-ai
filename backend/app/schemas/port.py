"""Port API schemas."""

from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMModel
from pydantic import Field


class PortCreate(ORMModel):
    name: str = Field(min_length=1, max_length=160)
    unlocode: str = Field(pattern=r"^[A-Za-z]{2}[A-Za-z0-9]{3}$")
    country_code: str = Field(pattern=r"^[A-Za-z]{2}$")
    location: str = Field(min_length=1, max_length=128, description="WKT POINT or PostGIS value")
    timezone: str = "UTC"
    active: bool = True
    handling_capability: str | None = None
    congestion_status: str | None = None
    operational_status: str = "operational"


class PortUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    unlocode: str | None = Field(default=None, pattern=r"^[A-Za-z]{2}[A-Za-z0-9]{3}$")
    country_code: str | None = Field(default=None, pattern=r"^[A-Za-z]{2}$")
    location: str | None = Field(default=None, min_length=1, max_length=128)
    timezone: str | None = None
    active: bool | None = None
    handling_capability: str | None = None
    congestion_status: str | None = None
    operational_status: str | None = None


class PortRead(PortCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
