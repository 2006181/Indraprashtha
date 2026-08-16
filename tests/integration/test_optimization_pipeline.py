import pytest
from railway_twin.optimization.optimizer import TrafficOptimizer
from railway_twin.optimization.safety_validator import SafetyValidator

def test_full_optimization_and_safety_pipeline(sample_network, sample_trains):
    for t in sample_trains.values():
        sample_network.register_train(t)

    optimizer = TrafficOptimizer(sample_network)
    validator = SafetyValidator(sample_network)

    # Initial conflicting plan
    trajectories = {
        "T101": [{"block_id": "B5", "enter_time": 200.0, "exit_time": 400.0}],
        "F201": [{"block_id": "B5", "enter_time": 200.0, "exit_time": 400.0}]
    }

    # 1. Verify raw input plan fails safety validation
    unvalidated_report = validator.validate_plan(trajectories)
    assert unvalidated_report.is_safe is False

    # 2. Run Traffic Optimizer to produce resolved schedule
    opt_result = optimizer.optimize(trajectories)
    assert opt_result.is_valid is True

    # 3. Verify optimized schedule passes deterministic Safety Validation (INVARIANT 6)
    validated_report = validator.validate_plan(opt_result.schedule_plan)
    assert validated_report.is_safe is True
    assert len(validated_report.violations) == 0
