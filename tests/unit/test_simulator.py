import pytest
from railway_twin.simulation.simulator import TrainSimulator
from railway_twin.digital_twin.train import Train, TrainStatus

def test_simulator_stepping(sample_network):
    t = Train("T101", "Rajdhani", route=["B1", "B2", "B3"])
    sample_network.register_train(t)
    sim = TrainSimulator(sample_network, seed=42)

    # Initial state
    assert t.status == TrainStatus.SCHEDULED

    # Step simulator
    sim.step(10.0)
    assert t.status == TrainStatus.RUNNING
    assert t.current_block_id == "B1"
    assert t.current_speed > 0

def test_delay_injection_in_simulator(sample_network):
    t = Train("T101", "Rajdhani", route=["B1", "B2", "B3"])
    sample_network.register_train(t)
    sim = TrainSimulator(sample_network)

    sim.inject_delay("T101", 10.0)
    assert t.delay_minutes == 10.0
