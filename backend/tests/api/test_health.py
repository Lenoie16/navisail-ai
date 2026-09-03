from app.main import app
from fastapi.testclient import TestClient


def test_health() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]


def test_version() -> None:
    response = TestClient(app).get("/api/v1/version")
    assert response.status_code == 200
    assert response.json()["version"] == "0.1.0-rc.1"
