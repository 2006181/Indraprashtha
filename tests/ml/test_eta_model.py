import pytest
from railway_twin.ml.eta_model import ETAPredictionModel
from railway_twin.ml.preprocessing import RawFeatureInput

def test_eta_prediction_sanity():
    model = ETAPredictionModel()
    raw = RawFeatureInput(
        speed=100.0,
        distance=50.0,
        train_type="EXPRESS",
        current_delay=10.0,
        block_id="B1",
        time_of_day_seconds=36000.0
    )
    eta = model.predict_eta_minutes(raw)
    
    # 50km / 100km/h = 30 min + 10 min delay = 40 min
    assert isinstance(eta, float)
    assert eta >= 35.0 and eta <= 45.0

def test_eta_zero_speed_fallback():
    model = ETAPredictionModel()
    raw = RawFeatureInput(
        speed=0.0,  # Zero speed train
        distance=10.0,
        train_type="PASSENGER",
        current_delay=0.0,
        block_id="B1",
        time_of_day_seconds=36000.0
    )
    # Model should use fallback minimum speed without crashing or returning infinity
    eta = model.predict_eta_minutes(raw)
    assert eta > 0.0
    assert not pytest.approx(eta) == float('inf')
