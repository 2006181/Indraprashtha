import pytest
from railway_twin.optimization.constraints import ConstraintEvaluator

def test_hard_constraint_single_occupancy_violation(sample_network):
    evaluator = ConstraintEvaluator(sample_network)
    
    plan_with_violation = {
        "T101": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}],
        "T102": [{"block_id": "B5", "enter_time": 200.0, "exit_time": 400.0}]
    }

    violations = evaluator.evaluate_schedule_plan(plan_with_violation)
    assert len(violations) > 0
    names = [v.constraint_name for v in violations]
    assert "SINGLE_BLOCK_OCCUPANCY" in names or "MINIMUM_HEADWAY" in names

def test_hard_constraint_unavailable_block_violation(sample_network):
    evaluator = ConstraintEvaluator(sample_network)
    sample_network.blocks["B5"].set_available(False)

    plan = {
        "T101": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 200.0}]
    }

    violations = evaluator.evaluate_schedule_plan(plan)
    assert len(violations) > 0
    assert any(v.constraint_name == "BLOCK_AVAILABILITY" for v in violations)
