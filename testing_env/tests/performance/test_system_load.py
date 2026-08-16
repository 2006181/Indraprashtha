import pytest
from railway_twin.simulation.simulator import TrainSimulator
from tests.fixtures.railway_network import create_complex_network
from tests.fixtures.sample_trains import create_sample_train_fleet

def test_system_stability_under_heavy_load():
    net = create_complex_network()
    fleet = create_sample_train_fleet(count=50)  # 50 trains stress test
    for t in fleet:
        net.register_train(t)

    sim = TrainSimulator(net, seed=42)

    # 100 simulation steps
    for _ in range(100):
        sim.step(5.0)

    assert len(net.trains) == 50
    assert len(sim.history) == 5000  # 50 trains * 100 frames
