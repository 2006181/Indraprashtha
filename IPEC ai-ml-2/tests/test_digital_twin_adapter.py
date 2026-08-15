import pytest
from ml.digital_twin_adapter import DigitalTwinAdapter

def test_digital_twin_adapter():
    adapter = DigitalTwinAdapter()
    sample_state = {
        "timestamp": "2026-08-16T00:00:00Z",
        "trains": [
            {
                "train_id": "12673",
                "train_type": "Express",
                "station_code": "MAS",
                "delay_minutes": 10.0,
                "scheduled_travel_time_mins": 120.0
            },
            {
                "train_id": "12674",
                "train_type": "Superfast",
                "station_code": "MAS",
                "delay_minutes": 2.0,
                "scheduled_travel_time_mins": 100.0
            }
        ]
    }
    result = adapter.predict_from_digital_twin_state(sample_state)

    assert result["total_trains_processed"] == 2
    assert len(result["predictions"]) == 2
    assert "optimizer_input" in result
    assert len(result["conflicts"]) == 1
