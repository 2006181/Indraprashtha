import pytest
from railway_twin.simulation.simulator import TrainSimulator
from railway_twin.digital_twin.train import Train
from railway_twin.optimization.safety_validator import SafetyValidator

def test_scenario_block_failure(sample_network):
    t1 = Train("T101", "Express Alpha", route=["B1", "B2", "B3", "B4", "B5"])
    sample_network.register_train(t1)

    sim = TrainSimulator(sample_network)
    
    # Block B3 fails
    sim.inject_block_failure("B3")
    assert sample_network.blocks["B3"].is_available is False
    assert sample_network.blocks["B3"].state.value == "BLOCKED"

    # Safety validator should reject any plan routing through B3
    validator = SafetyValidator(sample_network)
    plan_through_b3 = {"T101": [{"block_id": "B3", "enter_time": 100.0, "exit_time": 200.0}]}
    report = validator.validate_plan(plan_through_b3)
    
    assert report.is_safe is False
    assert report.invariant_results["INVARIANT_3_BLOCK_AVAILABILITY"] is False
