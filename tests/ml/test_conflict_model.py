import pytest
from railway_twin.ml.conflict_model import ConflictPredictionModel

def test_conflict_probability():
    model = ConflictPredictionModel()
    
    # Same block, simultaneous ETA -> High conflict prob
    prob_same = model.predict_conflict_probability("B5", "B5", 300.0, 310.0, min_headway_sec=180.0)
    assert prob_same >= 0.90
    assert model.is_conflict_predicted(prob_same) is True

    # Different blocks -> Low conflict prob
    prob_diff = model.predict_conflict_probability("B5", "B6", 300.0, 310.0)
    assert prob_diff < 0.10
    assert model.is_conflict_predicted(prob_diff) is False

def test_conflict_model_evaluation_metrics():
    model = ConflictPredictionModel()
    y_true = [1, 1, 1, 0, 0, 0]
    y_pred = [1, 1, 1, 0, 0, 0]  # Perfect classification
    
    metrics = model.evaluate_metrics(y_true, y_pred)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["fnr"] == 0.0  # Zero False Negative Rate required for safety!
