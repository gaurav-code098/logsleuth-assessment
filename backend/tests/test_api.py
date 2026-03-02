import pytest
from app.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the API is up and running."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"

def test_missing_session_id(client):
    """Test Interface Safety: Ensure API rejects requests without a session ID."""
    response = client.post("/api/logs", json={"raw_log": "Error: Timeout"})
    assert response.status_code == 400
    assert "Missing X-Session-ID" in response.json["detail"]

def test_invalid_payload(client):
    """Test Interface Safety: Ensure Pydantic catches malformed JSON."""
    response = client.post(
        "/api/logs", 
        headers={"X-Session-ID": "test-session-123"},
        json={"wrong_key": "Error"} # Missing 'raw_log'
    )
    assert response.status_code == 422