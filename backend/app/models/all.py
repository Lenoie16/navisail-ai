"""SQLAlchemy 2 persistence model for the Navisail maritime domain."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum, StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.db.types import GeographyLineString, GeographyPoint, UTCDateTime, UUIDType


class ModelBase(DeclarativeBase):
    """Base class used by all application entities."""


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class Entity(ModelBase, Timestamped):
    """Common UUID identity and timestamps."""

    __abstract__ = True
    id: Mapped[UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid4)


class ShipmentStatus(StrEnum):
    planned = "planned"
    booked = "booked"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"


class VesselStatus(StrEnum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"


class ContractStatus(StrEnum):
    draft = "draft"
    active = "active"
    expired = "expired"
    terminated = "terminated"


class RecommendationStatus(StrEnum):
    proposed = "proposed"
    approved = "approved"
    rejected = "rejected"
    executed = "executed"


class ApprovalStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ExecutionStatus(StrEnum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


def enum_type(enum: type[Enum]) -> SAEnum:
    return SAEnum(enum, name=enum.__name__.lower(), native_enum=True, validate_strings=True)


class Commodity(Entity):
    __tablename__ = "commodities"

    name: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    hazardous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    shipments: Mapped[list[Shipment]] = relationship(back_populates="commodity")


class Plant(Entity):
    __tablename__ = "plants"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    address: Mapped[str | None] = mapped_column(String(500))
    location: Mapped[str | None] = mapped_column(GeographyPoint)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    shipments: Mapped[list[Shipment]] = relationship(back_populates="plant")

    __table_args__ = (Index("ix_plants_location_gist", "location", postgresql_using="gist"),)


class Origin(Entity):
    __tablename__ = "origins"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    location: Mapped[str | None] = mapped_column(GeographyPoint)
    shipments: Mapped[list[Shipment]] = relationship(back_populates="origin")

    __table_args__ = (Index("ix_origins_location_gist", "location", postgresql_using="gist"),)


class Port(Entity):
    __tablename__ = "ports"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    unlocode: Mapped[str] = mapped_column(String(5), nullable=False, unique=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    location: Mapped[str] = mapped_column(GeographyPoint, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    handling_capability: Mapped[str | None] = mapped_column(String(500))
    congestion_status: Mapped[str | None] = mapped_column(String(80))
    operational_status: Mapped[str] = mapped_column(
        String(80), default="operational", nullable=False
    )
    berths: Mapped[list[Berth]] = relationship(back_populates="port", cascade="all, delete-orphan")
    origin_shipments: Mapped[list[Shipment]] = relationship(
        back_populates="origin_port", foreign_keys="Shipment.origin_port_id"
    )
    destination_shipments: Mapped[list[Shipment]] = relationship(
        back_populates="destination_port", foreign_keys="Shipment.destination_port_id"
    )
    origin_routes: Mapped[list[Route]] = relationship(
        back_populates="origin_port", foreign_keys="Route.origin_port_id"
    )
    destination_routes: Mapped[list[Route]] = relationship(
        back_populates="destination_port", foreign_keys="Route.destination_port_id"
    )

    __table_args__ = (
        Index("ix_ports_location_gist", "location", postgresql_using="gist"),
        CheckConstraint("length(unlocode) = 5", name="ck_ports_unlocode_length"),
    )


class Berth(Entity):
    __tablename__ = "berths"

    port_id: Mapped[UUID] = mapped_column(
        ForeignKey("ports.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    max_loa_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    max_beam_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    max_draft_m: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    max_dwt_tonnes: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cargo_constraints: Mapped[str | None] = mapped_column(Text)
    operational_restrictions: Mapped[str | None] = mapped_column(Text)
    working_capability: Mapped[str | None] = mapped_column(String(500))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    port: Mapped[Port] = relationship(back_populates="berths")

    __table_args__ = (
        UniqueConstraint("port_id", "code", name="uq_berths_port_code"),
        CheckConstraint("max_draft_m IS NULL OR max_draft_m > 0", name="ck_berths_draft_positive"),
    )


class Vessel(Entity):
    __tablename__ = "vessels"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    imo_number: Mapped[str] = mapped_column(String(7), nullable=False, unique=True)
    vessel_type: Mapped[str] = mapped_column(String(80), nullable=False)
    operator: Mapped[str | None] = mapped_column(String(160))
    deadweight_tonnes: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    loa_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    beam_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    max_draft_m: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    speed_knots: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    fuel_characteristics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[VesselStatus] = mapped_column(
        enum_type(VesselStatus), default=VesselStatus.active
    )
    positions: Mapped[list[VesselPosition]] = relationship(
        back_populates="vessel", cascade="all, delete-orphan"
    )
    voyages: Mapped[list[Voyage]] = relationship(back_populates="vessel")

    __table_args__ = (
        CheckConstraint("length(imo_number) = 7", name="ck_vessels_imo_length"),
        CheckConstraint(
            "deadweight_tonnes IS NULL OR deadweight_tonnes > 0",
            name="ck_vessels_deadweight_positive",
        ),
        Index("ix_vessels_status", "status"),
    )


class VesselPosition(Entity):
    __tablename__ = "vessel_positions"

    vessel_id: Mapped[UUID] = mapped_column(
        ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False
    )
    observed_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    position: Mapped[str] = mapped_column(GeographyPoint, nullable=False)
    speed_knots: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    heading_degrees: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    vessel: Mapped[Vessel] = relationship(back_populates="positions")

    __table_args__ = (
        Index("ix_vessel_positions_vessel_observed", "vessel_id", "observed_at"),
        Index("ix_vessel_positions_position_gist", "position", postgresql_using="gist"),
        CheckConstraint(
            "heading_degrees IS NULL OR (heading_degrees >= 0 AND heading_degrees < 360)",
            name="ck_vessel_positions_heading",
        ),
    )


class Route(Entity):
    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    origin_port_id: Mapped[UUID] = mapped_column(ForeignKey("ports.id"), nullable=False)
    destination_port_id: Mapped[UUID] = mapped_column(ForeignKey("ports.id"), nullable=False)
    geometry: Mapped[str | None] = mapped_column(GeographyLineString)
    distance_nm: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    origin_port: Mapped[Port] = relationship(
        back_populates="origin_routes", foreign_keys=[origin_port_id]
    )
    destination_port: Mapped[Port] = relationship(
        back_populates="destination_routes", foreign_keys=[destination_port_id]
    )
    voyages: Mapped[list[Voyage]] = relationship(back_populates="route")

    __table_args__ = (
        CheckConstraint("origin_port_id <> destination_port_id", name="ck_routes_distinct_ports"),
        Index("ix_routes_geometry_gist", "geometry", postgresql_using="gist"),
    )


class Voyage(Entity):
    __tablename__ = "voyages"

    vessel_id: Mapped[UUID] = mapped_column(ForeignKey("vessels.id"), nullable=False)
    route_id: Mapped[UUID] = mapped_column(ForeignKey("routes.id"), nullable=False)
    voyage_number: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    departure_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    arrival_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    vessel: Mapped[Vessel] = relationship(back_populates="voyages")
    route: Mapped[Route] = relationship(back_populates="voyages")

    __table_args__ = (
        CheckConstraint(
            "arrival_at IS NULL OR arrival_at >= departure_at",
            name="ck_voyages_arrival_after_departure",
        ),
    )


class Shipment(Entity):
    __tablename__ = "shipments"

    reference: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    commodity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commodities.id", ondelete="RESTRICT")
    )
    plant_id: Mapped[UUID | None] = mapped_column(ForeignKey("plants.id", ondelete="RESTRICT"))
    origin_id: Mapped[UUID | None] = mapped_column(ForeignKey("origins.id", ondelete="RESTRICT"))
    origin_port_id: Mapped[UUID | None] = mapped_column(ForeignKey("ports.id", ondelete="RESTRICT"))
    destination_port_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ports.id", ondelete="RESTRICT")
    )
    quantity_tonnes: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    status: Mapped[ShipmentStatus] = mapped_column(
        enum_type(ShipmentStatus), default=ShipmentStatus.planned, nullable=False
    )
    planned_departure_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    planned_arrival_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    commodity: Mapped[Commodity | None] = relationship(back_populates="shipments")
    plant: Mapped[Plant | None] = relationship(back_populates="shipments")
    origin: Mapped[Origin | None] = relationship(back_populates="shipments")
    origin_port: Mapped[Port | None] = relationship(
        back_populates="origin_shipments", foreign_keys=[origin_port_id]
    )
    destination_port: Mapped[Port | None] = relationship(
        back_populates="destination_shipments", foreign_keys=[destination_port_id]
    )

    __table_args__ = (
        CheckConstraint("quantity_tonnes > 0", name="ck_shipments_quantity_positive"),
        CheckConstraint(
            "planned_arrival_at IS NULL OR planned_departure_at IS NULL OR "
            "planned_arrival_at >= planned_departure_at",
            name="ck_shipments_schedule",
        ),
        Index("ix_shipments_status", "status"),
        Index("ix_shipments_destination_port", "destination_port_id"),
    )


class Contract(Entity):
    __tablename__ = "contracts"

    contract_number: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    counterparty: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        enum_type(ContractStatus), default=ContractStatus.draft, nullable=False
    )
    valid_from: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(UTCDateTime())
    terms: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint(
            "valid_until IS NULL OR valid_until >= valid_from", name="ck_contracts_validity"
        ),
    )


class Inventory(Entity):
    __tablename__ = "inventory"

    plant_id: Mapped[UUID] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), nullable=False
    )
    commodity_id: Mapped[UUID] = mapped_column(
        ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False
    )
    quantity_tonnes: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    as_of: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    plant: Mapped[Plant] = relationship()
    commodity: Mapped[Commodity] = relationship()
    __table_args__ = (
        UniqueConstraint("plant_id", "commodity_id", name="uq_inventory_plant_commodity"),
        CheckConstraint("quantity_tonnes >= 0", name="ck_inventory_quantity_nonnegative"),
    )


class DecisionSession(Entity):
    __tablename__ = "decision_sessions"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    context: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    __table_args__ = (
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at", name="ck_decision_sessions_dates"
        ),
    )


class MaritimeStateSnapshot(Entity):
    __tablename__ = "maritime_state_snapshots"

    decision_session_id: Mapped[UUID | None] = mapped_column(ForeignKey("decision_sessions.id"))
    captured_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    decision_session: Mapped[DecisionSession | None] = relationship()


class Recommendation(Entity):
    __tablename__ = "recommendations"

    decision_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_sessions.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RecommendationStatus] = mapped_column(
        enum_type(RecommendationStatus), default=RecommendationStatus.proposed, nullable=False
    )
    decision_session: Mapped[DecisionSession] = relationship()


class Approval(Entity):
    __tablename__ = "approvals"

    recommendation_id: Mapped[UUID] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False
    )
    approver: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        enum_type(ApprovalStatus), default=ApprovalStatus.pending, nullable=False
    )
    decided_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    recommendation: Mapped[Recommendation] = relationship()


class Execution(Entity):
    __tablename__ = "executions"

    recommendation_id: Mapped[UUID] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ExecutionStatus] = mapped_column(
        enum_type(ExecutionStatus), default=ExecutionStatus.pending, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    recommendation: Mapped[Recommendation] = relationship()


class AuditRecord(Entity):
    __tablename__ = "audit_records"

    actor: Mapped[str] = mapped_column(String(160), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(UUIDType())
    occurred_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=lambda: datetime.now(UTC), nullable=False
    )
    details: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index("ix_audit_records_entity", "entity_type", "entity_id"),)


__all__ = [
    "Approval",
    "ApprovalStatus",
    "AuditRecord",
    "Berth",
    "Commodity",
    "Contract",
    "ContractStatus",
    "DecisionSession",
    "Execution",
    "ExecutionStatus",
    "Inventory",
    "MaritimeStateSnapshot",
    "ModelBase",
    "Origin",
    "Plant",
    "Port",
    "Recommendation",
    "RecommendationStatus",
    "Route",
    "Shipment",
    "ShipmentStatus",
    "Vessel",
    "VesselPosition",
    "VesselStatus",
    "Voyage",
]
