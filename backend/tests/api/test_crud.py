from collections.abc import Generator

import pytest
from app.db.base import Base
from app.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)

    def override_db() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_port_crud_and_validation(client: TestClient) -> None:
    payload = {
        "name": "Port of Rotterdam",
        "unlocode": "NLRTM",
        "country_code": "NL",
        "location": "POINT (4.4777 51.9244)",
    }
    created = client.post("/api/v1/ports", json=payload)
    assert created.status_code == 201
    port_id = created.json()["id"]
    assert client.get(f"/api/v1/ports/{port_id}").json()["location"].startswith("POINT")
    updated = client.patch(f"/api/v1/ports/{port_id}", json={"active": False})
    assert updated.status_code == 200
    assert updated.json()["active"] is False
    assert client.delete(f"/api/v1/ports/{port_id}").status_code == 204
    assert client.get(f"/api/v1/ports/{port_id}").status_code == 404


def test_vessel_and_shipment_payload_validation(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/vessels",
            json={"name": "Bad", "imo_number": "12", "vessel_type": "Tanker"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/shipments",
            json={"reference": "S-1", "quantity_tonnes": -2},
        ).status_code
        == 422
    )
