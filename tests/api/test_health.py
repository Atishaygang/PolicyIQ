from fastapi.testclient import TestClient
from src.api.main import app
client = TestClient(app)

def test_health_returns_200():
    response = client.get('/health')
    assert response.status_code == 200

def test_health_response_body():
    response = client.get('/health')
    data = response.json()

    assert data["service"] == "PolicyIQ API"
    assert data["status"] == "running"
    assert data["version"] == "5.0"