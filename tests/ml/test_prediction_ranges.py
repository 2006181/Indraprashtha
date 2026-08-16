import pytest
import math
from railway_twin.ml.eta_model import ETAPredictionModel
from railway_twin.ml.delay_model import DelayPredictionModel
from railway_twin.ml.preprocessing import RawFeatureInput

def test_prediction_output_ranges():
    eta_model = ETAPredictionModel()
    delay_model = DelayPredictionModel()

    # Test extreme ranges
    inputs = [
        RawFeatureInput(1.0, 0.1, "EXPRESS", 0.0, "B1", 0.0),
        RawFeatureInput(160.0, 100.0, "FREIGHT", 120.0, "B1", 86400.0),
        RawFeatureInput(50.0, 20.0, "PASSENGER", 5.0, "B1", 43200.0)
    ]

    for raw in inputs:
        eta = eta_model.predict_eta_minutes(raw)
        assert not math.isnan(eta)
        assert not math.isinf(eta)
        assert eta >= 0.0

    for current_delay in [0.0, 10.0, 60.0, 300.0]:
        pred_delay = delay_model.predict_downstream_delay(current_delay, 0.8, 5)
        assert not math.isnan(pred_delay)
        assert not math.isinf(pred_delay)
        assert pred_delay >= 0.0
