import pytest
from railway_twin.simulation.simulator import TrainSimulator
from tests.fixtures.sample_trains import create_sample_train_fleet

def test_scenario_high_traffic_density(sample_network):
    fleet = create_sample_train_fleet(count=20)
    for t in fleet:
        sample_network.register_train(t)

    sim = TrainSimulator(sample_network, seed=42)

    # Step simulator for 30 cycles
    for _ in range(30):
        sim.step(10.0)

    # Ensure system state remains consistent and no crashes occur under 20 trains
    assert len(sim.history) > 0
    assert len(sample_network.trains) == 20
