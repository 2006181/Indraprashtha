import pytest
import pandas as pd
from pathlib import Path
from ml.data_loader import RailwayDataLoader

def test_data_loader_initialization():
    loader = RailwayDataLoader()
    assert loader.dataset_dir is not None

def test_load_all_datasets():
    loader = RailwayDataLoader()
    datasets = loader.load_all_datasets()
    assert "etrain_delays" in datasets
    assert "train_delay_prediction" in datasets
    assert "india_railway_stations" in datasets
    assert "exp_trains" in datasets
    assert "pass_trains" in datasets
    assert "sf_trains" in datasets
    assert "scheduling_excel" in datasets

    assert isinstance(datasets["etrain_delays"], pd.DataFrame)
    assert len(datasets["exp_trains"]) > 0
