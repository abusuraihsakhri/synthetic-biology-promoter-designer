"""FastAPI integration smoke tests and rejection behavior."""
from fastapi.testclient import TestClient
from agents.api import app


def test_api_evaluation_and_audit_endpoint():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "HEALTHY"
    response = client.post("/api/audit", json={
        "task_id": "API-01", "target_identifier": "KEY-01",
        "primary_metric": 20, "secondary_metric": 3,
        "status_descriptor": "NOMINAL"
    })
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    trail = client.get("/api/audit/logs")
    assert trail.status_code == 200
    assert trail.json()["verified"] is True
    assert len(trail.json()["audit_trail"]) >= 1


def test_api_rejects_nonfinite_and_sensitive_values():
    client = TestClient(app)
    nonfinite = client.post("/api/audit", json={
        "task_id": "API-02", "target_identifier": "KEY-02",
        "primary_metric": "inf"
    })
    assert nonfinite.status_code == 422
    sensitive = client.post("/api/audit", json={
        "task_id": "API-03", "target_identifier": "KEY-03",
        "primary_metric": 10, "attributes": {"raw": "Patient MRN-994827"}
    })
    assert sensitive.status_code == 422
    assert "Sensitive identifiers" in sensitive.json()["detail"]
