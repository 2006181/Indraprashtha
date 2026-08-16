import pytest
from railway_twin.optimization.conflict_detector import ConflictDetector

def test_conflict_detection_same_block(sample_network):
    detector = ConflictDetector(sample_network, min_headway_seconds=180.0)

    # Trajectories where T101 and T102 overlap in block B5
    trajectories = {
        "T101": [("B4", 100.0, 200.0), ("B5", 200.0, 400.0)],
        "T102": [("B4", 0.0, 100.0), ("B5", 250.0, 350.0)]
    }

    conflicts = detector.detect_conflicts(trajectories)
    assert len(conflicts) > 0
    resources = [c.resource_id for c in conflicts]
    assert "B5" in resources
    assert any(c.conflict_type in ("BLOCK_OCCUPANCY", "HEADWAY_VIOLATION") for c in conflicts)

def test_no_conflict_different_blocks(sample_network):
    detector = ConflictDetector(sample_network)
    trajectories = {
        "T101": [("B4", 100.0, 200.0)],
        "T102": [("B5", 100.0, 200.0)]
    }

    conflicts = detector.detect_conflicts(trajectories)
    assert len(conflicts) == 0
