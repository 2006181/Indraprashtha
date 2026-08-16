import pytest
from railway_twin.ml.preprocessing import RawFeatureInput, FeaturePreprocessor
from railway_twin.ml.eta_model import ETAPredictionModel
from railway_twin.ml.delay_model import DelayPredictionModel
from railway_twin.ml.conflict_model import ConflictPredictionModel

def test_full_ml_prediction_pipeline():
    prep = FeaturePreprocessor()
    eta_model = ETAPredictionModel()
    delay_model = DelayPredictionModel()
    conflict_model = ConflictPredictionModel()

    raw1 = RawFeatureInput(110.0, 30.0, "EXPRESS", 5.0, "B2", 36000.0)
    raw2 = RawFeatureInput(90.0, 30.0, "PASSENGER", 15.0, "B2", 36000.0)

    # 1. Validate & Preprocess
    assert prep.validate(raw1) and prep.validate(raw2)
    
    # 2. ETA Prediction
    eta1 = eta_model.predict_eta_minutes(raw1)
    eta2 = eta_model.predict_eta_minutes(raw2)

    # 3. Downstream Delay Prediction
    delay1 = delay_model.predict_downstream_delay(raw1.current_delay, 0.4, 10)
    delay2 = delay_model.predict_downstream_delay(raw2.current_delay, 0.4, 6)

    # 4. Conflict Risk Classification
    prob = conflict_model.predict_conflict_probability("B2", "B2", eta1 * 60.0, eta2 * 60.0)
    is_conflict = conflict_model.is_conflict_predicted(prob)

    assert eta1 > 0 and eta2 > 0
    assert delay1 > 0 and delay2 >= 15.0
    assert isinstance(is_conflict, bool)
