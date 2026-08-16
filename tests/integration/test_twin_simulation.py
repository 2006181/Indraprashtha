import pytest
from railway_twin.simulation.simulator import TrainSimulator
from railway_twin.digital_twin.train import Train

def test_twin_simulation_integration(sample_network):
    t1 = Train("T101", "Express 1", route=["B1", "B2", "B3"])
    t2 = Train("T102", "Express 2", route=["B4", "B5", "B6"])
    sample_network.register_train(t1)
    sample_network.register_train(t2)

    sim = TrainSimulator(sample_network, seed=42)

    # Step simulator for 100 seconds
    for _ in range(10):
        sim.step(10.0)

    # Check telemetry frame history recorded
    assert len(sim.history) > 0
    # Current telemetry captured from generator must be 100% consistent with Digital Twin
    current_frame = sim.telemetry_gen.capture_frame(sim.current_time_seconds, "T101")
    assert sim.telemetry_gen.is_consistent_with_twin(current_frame) is True
