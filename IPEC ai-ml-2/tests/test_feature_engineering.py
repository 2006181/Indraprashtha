import pytest
from ml.data_loader import RailwayDataLoader
from ml.feature_engineering import build_unified_ml_features, parse_time_to_minutes

def test_parse_time_to_minutes():
    assert parse_time_to_minutes("09:45", day=1) == 585.0
    assert parse_time_to_minutes("01:15", day=2) == 1440.0 + 75.0
    assert parse_time_to_minutes("Source", day=1) != parse_time_to_minutes("Source", day=1)  # NaN check

def test_feature_engineering_pipeline():
    loader = RailwayDataLoader()
    datasets = loader.load_all_datasets()
    df_eta, df_delay, df_conflict = build_unified_ml_features(datasets)

    assert not df_eta.empty
    assert not df_delay.empty
    assert not df_conflict.empty
    assert "target_eta_minutes" in df_eta.columns
    assert "target_delay_minutes" in df_delay.columns
    assert "is_conflict" in df_conflict.columns
