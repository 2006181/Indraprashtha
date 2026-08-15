import pytest
from ml.prediction_service import PredictionService

def test_prediction_service_eta():
    service = PredictionService()
    res = service.predict_eta(
        train_id="12673",
        train_type="Express",
        station_code="MAS",
        scheduled_travel_time_mins=120.0,
        distance_kms=100.0,
        historical_avg_delay=10.0
    )
    assert "train_id" in res
    assert "predicted_eta_minutes" in res
    assert res["predicted_eta_minutes"] > 0.0

def test_prediction_service_delay():
    service = PredictionService()
    res = service.predict_delay(
        train_id="12673",
        train_type="Express",
        station_code="MAS",
        historical_avg_delay=15.0
    )
    assert "train_id" in res
    assert "predicted_delay_minutes" in res
    assert res["predicted_delay_minutes"] >= 0.0

def test_prediction_service_conflict():
    service = PredictionService()
    res = service.predict_conflict(
        train_id_a="12673",
        train_id_b="12674",
        station_code="MAS",
        scheduled_gap_mins=3.0,
        time_difference_mins=3.0,
        delay_a=15.0,
        delay_b=2.0
    )
    assert res["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert 0.0 <= res["conflict_probability"] <= 1.0

def test_prediction_service_all():
    service = PredictionService()
    res = service.predict_all(
        train_id="12673",
        train_type="Express",
        station_code="MAS",
        conflict_check_train_id="12674"
    )
    assert "eta" in res
    assert "delay" in res
    assert "conflict" in res
    assert "optimizer_payload" in res
