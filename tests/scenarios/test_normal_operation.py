import pytest
from railway_twin.simulation.simulator import TrainSimulator
from railway_twin.digital_twin.train import Train

def test_scenario_normal_operation(sample_network):
    t1 = Train("T101", "Express Alpha", route=["B1", "B2", "B3", "B4"])
    t2 = Train("T102", "Express Beta", route=["B6", "B7", "B8", "B9"])
    sample_network.register_train(t1)
    sample_network.register_train(t2)

    sim = TrainSimulator(sample_network)
    for _ in range(20):
        sim.step(10.0)

    # In normal operation with staggered blocks, no train should be delayed or stopped
    assert t1.delay_minutes == 0.0
    assert t2.delay_minutes == 0.0
