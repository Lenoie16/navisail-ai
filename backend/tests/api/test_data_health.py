from app.main import app
from fastapi.testclient import TestClient


def test_data_health_endpoints_are_read_only_and_typed() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/data-health")
    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert client.get("/api/v1/data-health/sources").json() == []
