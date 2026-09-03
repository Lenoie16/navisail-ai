from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.db.base import Base
from app.db.seeds import seed_reference_data
from app.models.all import Commodity, Plant, Port, Shipment, ShipmentStatus, Vessel
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db
    Base.metadata.drop_all(engine)


def test_reference_seed_is_repeatable_and_relationships_load(session: Session) -> None:
    seed_reference_data(session)
    seed_reference_data(session)
    port = session.query(Port).filter_by(unlocode="NLRTM").one()
    assert len(port.berths) == 1
    assert port.location == "POINT (4.4777 51.9244)"
    assert port.created_at.tzinfo is not None
    assert session.query(Commodity).count() == 1
    assert session.query(Plant).count() == 1


def test_shipment_fk_and_positive_quantity_constraint(session: Session) -> None:
    vessel = Vessel(name="Aurora", imo_number="1234567", vessel_type="Bulk carrier")
    session.add(vessel)
    session.commit()
    shipment = Shipment(
        reference="SHP-001",
        quantity_tonnes=Decimal("10.5"),
        status=ShipmentStatus.planned,
    )
    session.add(shipment)
    session.commit()
    assert shipment.id is not None
    assert shipment.status is ShipmentStatus.planned
    assert isinstance(shipment.created_at, datetime)
    assert shipment.created_at.tzinfo == UTC

    session.add(Shipment(reference="SHP-002", quantity_tonnes=Decimal("-1")))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
