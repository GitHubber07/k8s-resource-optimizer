import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_optimize_endpoint():
    payload = [
        {
            "deployment": "api-service",
            "cpu_request": 1000,
            "cpu_usage_avg": 180,
            "memory_request": 2048,
            "memory_usage_avg": 700
        }
    ]
    response = client.post("/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["deployment"] == "api-service"
    assert "recommended_cpu" in data[0]
    assert "recommended_memory" in data[0]
    assert "reason" in data[0]

def test_optimize_empty_input():
    response = client.post("/optimize", json=[])
    assert response.status_code == 400
