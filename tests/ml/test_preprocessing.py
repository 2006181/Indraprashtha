import pytest
from railway_twin.ml.preprocessing import FeaturePreprocessor, RawFeatureInput

def test_preprocessing_valid_input():
    prep = FeaturePreprocessor()
    raw = RawFeatureInput(
        speed=100.0,
        distance=10.0,
        train_type="EXPRESS",
        current_delay=5.0,
        block_id="B1",
        time_of_day_seconds=36000.0
    )
    assert prep.validate(raw) is True
    vec = prep.preprocess(raw)
    assert len(vec) == 7  # 4 norm numeric + 3 one-hot train_types

def test_preprocessing_invalid_inputs():
    prep = FeaturePreprocessor()
    raw_neg_speed = RawFeatureInput(speed=-10.0, distance=5.0, train_type="EXPRESS", current_delay=0.0, block_id="B1", time_of_day_seconds=0.0)
    assert prep.validate(raw_neg_speed) is False

    with pytest.raises(ValueError):
        prep.preprocess(raw_neg_speed)
