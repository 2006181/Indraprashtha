import pytest
from railway_twin.optimization.conflict_detector import ConflictDetector

def test_scenario_crossing_conflict_detection(sample_network):
    detector = ConflictDetector(sample_network)
    
    # Train A and Train B enter junction block B5 at overlapping time
    trajectories = {
        "Train_Up": [{"block_id": "B5", "enter_time": 500.0, "exit_time": 700.0}],
        "Train_Down": [{"block_id": "B5", "enter_time": 600.0, "exit_time": 800.0}]
    }

    conflicts = detector.detect_conflicts(trajectories)
    assert len(conflicts) > 0
    assert conflicts[0].resource_id == "B5"
