import pytest
from fastapi.testclient import TestClient
from ml.prediction_api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"

def test_models_endpoint():
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data

def test_predict_eta_endpoint():
    payload = {
        "train_id": "12673",
        "train_type": "Express",
        "station_code": "MAS",
        "scheduled_travel_time_mins": 120.0,
        "distance_kms": 100.0,
        "historical_avg_delay": 15.0
    }
    response = client.post("/predict/eta", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["train_id"] == "12673"
    assert "predicted_eta_minutes" in data

def test_predict_delay_endpoint():
    payload = {
        "train_id": "12673",
        "train_type": "Express",
        "station_code": "MAS",
        "historical_avg_delay": 15.0
    }
    response = client.post("/predict/delay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_delay_minutes" in data

def test_predict_conflict_endpoint():
    payload = {
        "train_id_a": "12673",
        "train_id_b": "12674",
        "station_code": "MAS",
        "scheduled_gap_mins": 4.0,
        "time_difference_mins": 4.0,
        "delay_a": 10.0,
        "delay_b": 1.0
    }
    response = client.post("/predict/conflict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conflict_probability" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_predict_all_endpoint():
    payload = {
        "train_id": "12673",
        "train_type": "Express",
        "station_code": "MAS",
        "conflict_check_train_id": "12674"
    }
    response = client.post("/predict/all", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "eta" in data
    assert "delay" in data
    assert "conflict" in data
    assert "optimizer_payload" in data
