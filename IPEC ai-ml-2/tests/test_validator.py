import pytest
from ml.data_loader import RailwayDataLoader
from ml.data_validator import DataValidator

def test_data_validator():
    loader = RailwayDataLoader()
    validator = DataValidator(loader)
    report = validator.validate_all()

    assert "summary" in report
    assert "datasets" in report
    assert report["summary"]["total_files_validated"] > 0
    assert "etrain_delays.csv" in report["datasets"]
