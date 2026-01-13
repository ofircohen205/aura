
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_events_endpoint():
    response = client.post(
        "/api/v1/events/",
        json={"source": "pytest", "type": "test", "data": {"foo": "bar"}}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "received"

def test_audit_endpoint():
    response = client.get("/api/v1/audit/?repo_path=./")
    assert response.status_code == 200
    assert response.json()["status"] == "audit_started"
