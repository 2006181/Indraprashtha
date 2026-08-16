import pytest
from railway_twin.ml.delay_model import DelayPredictionModel

def test_delay_prediction_logic():
    model = DelayPredictionModel()
    
    # High traffic density should increase delay
    delay_low_traffic = model.predict_downstream_delay(10.0, traffic_density=0.1, train_priority=5)
    delay_high_traffic = model.predict_downstream_delay(10.0, traffic_density=0.9, train_priority=5)
    
    assert delay_high_traffic > delay_low_traffic

    # Blocked section scenario
    delay_blocked = model.predict_downstream_delay(10.0, traffic_density=0.5, train_priority=5, is_section_blocked=True)
    assert delay_blocked >= 30.0

def test_delay_model_metrics():
    model = DelayPredictionModel()
    y_true = [5.0, 10.0, 15.0, 20.0]
    y_pred = [4.8, 10.2, 14.5, 20.5]
    
    mae, rmse, r2 = model.evaluate_metrics(y_true, y_pred)
    assert mae < 1.0
    assert rmse < 1.0
    assert r2 > 0.95
