import pytest
from railway_twin.optimization.safety_validator import SafetyValidator

def test_safety_invariant_1_same_block_rejected(sample_network):
    validator = SafetyValidator(sample_network)
    unsafe_plan = {
        "T1": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}],
        "T2": [{"block_id": "B5", "enter_time": 200.0, "exit_time": 400.0}]
    }
    report = validator.validate_plan(unsafe_plan)
    assert report.is_safe is False
    assert report.invariant_results["INVARIANT_1_BLOCK_SINGLE_OCCUPANCY"] is False

def test_safety_invariant_2_headway_violation_rejected(sample_network):
    validator = SafetyValidator(sample_network, min_headway_sec=180.0)
    headway_violation_plan = {
        "T1": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}],
        "T2": [{"block_id": "B5", "enter_time": 160.0, "exit_time": 360.0}]  # 60s headway < 180s required
    }
    report = validator.validate_plan(headway_violation_plan)
    assert report.is_safe is False
    assert report.invariant_results["INVARIANT_2_MINIMUM_HEADWAY"] is False

def test_safety_invariant_3_blocked_route_rejected(sample_network):
    validator = SafetyValidator(sample_network)
    sample_network.blocks["B5"].set_available(False)
    blocked_plan = {
        "T1": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 200.0}]
    }
    report = validator.validate_plan(blocked_plan)
    assert report.is_safe is False
    assert report.invariant_results["INVARIANT_3_BLOCK_AVAILABILITY"] is False

def test_safety_invariant_4_occupied_platform_rejected(sample_network):
    validator = SafetyValidator(sample_network)
    platform_conflict_plan = {
        "T1": [{"block_id": "B1", "enter_time": 100.0, "exit_time": 300.0, "platform_id": "P1"}],
        "T2": [{"block_id": "B2", "enter_time": 150.0, "exit_time": 350.0, "platform_id": "P1"}]
    }
    report = validator.validate_plan(platform_conflict_plan)
    assert report.is_safe is False
    assert report.invariant_results["INVARIANT_4_PLATFORM_AVAILABILITY"] is False

def test_safety_invariant_7_ai_recommendation_override_prevention(sample_network):
    validator = SafetyValidator(sample_network)
    ai_recommendation = {"action": "OVERRIDE_AND_PROCEED", "confidence": 0.99}
    unsafe_plan = {
        "T1": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}],
        "T2": [{"block_id": "B5", "enter_time": 150.0, "exit_time": 350.0}]
    }
    
    # Assert deterministic validator REJECTS AI recommendation when plan violates safety!
    passed = validator.validate_ai_recommendation(ai_recommendation, unsafe_plan)
    assert passed is False
