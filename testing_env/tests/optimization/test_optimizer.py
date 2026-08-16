import pytest
from railway_twin.optimization.optimizer import TrafficOptimizer

def test_optimizer_resolves_conflict(sample_network, sample_trains):
    for t in sample_trains.values():
        sample_network.register_train(t)

    optimizer = TrafficOptimizer(sample_network)

    # Input conflicting plan: T101 (Express, P10) and F201 (Freight, P3) both in B4 at t=200-400
    trajectories = {
        "T101": [{"block_id": "B4", "enter_time": 200.0, "exit_time": 400.0}],
        "F201": [{"block_id": "B4", "enter_time": 200.0, "exit_time": 400.0}]
    }

    res = optimizer.optimize(trajectories)
    assert res.is_valid is True
    assert len(res.strategies) > 0
    # Lower priority Freight should be held for Express
    strat = res.strategies[0]
    assert strat.affected_train_id == "F201"
    assert res.runtime_seconds < 2.0
