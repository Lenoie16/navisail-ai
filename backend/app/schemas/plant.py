"""Plant API schemas."""

from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMModel
from pydantic import Field


class PlantCreate(ORMModel):
    name: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    address: str | None = None
    location: str | None = Field(default=None, max_length=128)
    active: bool = True


class PlantUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    code: str | None = Field(default=None, min_length=1, max_length=40)
    address: str | None = None
    location: str | None = Field(default=None, max_length=128)
    active: bool | None = None


class PlantRead(PlantCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
