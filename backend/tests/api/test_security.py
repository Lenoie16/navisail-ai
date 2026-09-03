from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_are_present() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Content-Security-Policy"].startswith("default-src")


def test_execution_rejects_principal_without_booking_permission() -> None:
    response = TestClient(app).post(
        "/api/v1/execution/executions",
        json={"recommendation_id": "rec-1", "user": "alice"},
        headers={"X-Navisail-User": "alice", "X-Navisail-Role": "leadership"},
    )
    assert response.status_code == 403


def test_execution_rejects_body_identity_spoofing() -> None:
    response = TestClient(app).post(
        "/api/v1/execution/executions",
        json={"recommendation_id": "rec-1", "user": "alice"},
        headers={"X-Navisail-User": "bob", "X-Navisail-Role": "operations"},
    )
    assert response.status_code == 403
