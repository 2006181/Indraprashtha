import time
import pytest
from railway_twin.optimization.optimizer import TrafficOptimizer
from tests.fixtures.railway_network import create_complex_network
from tests.fixtures.sample_trains import create_sample_train_fleet

def test_optimizer_runtime_performance():
    net = create_complex_network()
    fleet = create_sample_train_fleet(count=5)
    for t in fleet:
        net.register_train(t)

    optimizer = TrafficOptimizer(net)

    # Generate 5 train trajectories with potential conflicts
    trajectories = {}
    for i, t in enumerate(fleet):
        enter = i * 400.0
        trajectories[t.train_id] = [
            {"block_id": "B5", "enter_time": enter, "exit_time": enter + 300.0}
        ]

    start = time.time()
    result = optimizer.optimize(trajectories)
    elapsed = time.time() - start

    # Optimization must complete under 2.0 seconds
    assert elapsed < 2.0
    assert result.is_valid is True
