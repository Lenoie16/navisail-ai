from app.main import app
from fastapi.testclient import TestClient


def test_snapshot_create_load_session_and_compare() -> None:
    client = TestClient(app)
    session_id = "00000000-0000-0000-0000-000000000099"
    component = {
        "timestamp": "2025-01-02T00:00:00Z",
        "source": "synthetic-engine",
        "quality": 1,
        "freshness": {
            "state": "FRESH",
            "age_seconds": 0,
            "threshold_seconds": 900,
            "evaluated_at": "2025-01-02T00:00:00Z",
        },
        "status": "SYNTHETIC",
        "confidence": 1,
        "data": {"vessel_id": "v-1"},
    }
    body = {
        "decision_session_id": session_id,
        "version": 1,
        "generated_at": "2025-01-02T00:00:00Z",
        "effective_at": "2025-01-02T00:00:00Z",
        "components": {"ais": component},
    }
    first = client.post("/api/v1/maritime-state/snapshots", json=body)
    assert first.status_code == 201
    snapshot_id = first.json()["snapshot_id"]
    assert client.get(f"/api/v1/maritime-state/snapshots/{snapshot_id}").status_code == 200
    assert len(client.get(f"/api/v1/maritime-state/sessions/{session_id}/snapshots").json()) == 1

    changed_component = {**component, "data": {"vessel_id": "v-2"}}
    changed = {**body, "version": 2, "components": {"ais": changed_component}}
    second = client.post("/api/v1/maritime-state/snapshots", json=changed)
    assert second.status_code == 201
    diff = client.get(
        f"/api/v1/maritime-state/snapshots/{snapshot_id}/compare/{second.json()['snapshot_id']}"
    )
    assert diff.status_code == 200
    assert diff.json()["changed"] == ["ais"]
