import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# --------------------------------------------------
# SYSTEM HEALTH API TEST
# --------------------------------------------------
def test_health_check_endpoint():
    """Verifies that the /api/v1/health endpoint returns 200 OK and healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "HEALTHY" in data["database"]
    assert data["security"]["auth_mode"] == "JWT_BEARER"


# --------------------------------------------------
# ROOT ENDPOINT TEST
# --------------------------------------------------
def test_root_endpoint():
    """Verifies root URL redirects to system information and docs."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
