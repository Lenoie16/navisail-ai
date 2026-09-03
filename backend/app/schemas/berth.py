"""Berth API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.schemas.common import ORMModel
from pydantic import Field


class BerthCreate(ORMModel):
    port_id: UUID
    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=40)
    max_loa_m: Decimal | None = Field(default=None, gt=0)
    max_beam_m: Decimal | None = Field(default=None, gt=0)
    max_draft_m: Decimal | None = Field(default=None, gt=0)
    max_dwt_tonnes: Decimal | None = Field(default=None, gt=0)
    cargo_constraints: str | None = None
    operational_restrictions: str | None = None
    working_capability: str | None = None
    active: bool = True


class BerthUpdate(ORMModel):
    port_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    code: str | None = Field(default=None, min_length=1, max_length=40)
    max_loa_m: Decimal | None = Field(default=None, gt=0)
    max_beam_m: Decimal | None = Field(default=None, gt=0)
    max_draft_m: Decimal | None = Field(default=None, gt=0)
    max_dwt_tonnes: Decimal | None = Field(default=None, gt=0)
    cargo_constraints: str | None = None
    operational_restrictions: str | None = None
    working_capability: str | None = None
    active: bool | None = None


class BerthRead(BerthCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
