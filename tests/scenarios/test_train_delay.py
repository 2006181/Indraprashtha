import pytest
from railway_twin.simulation.simulator import TrainSimulator
from railway_twin.simulation.events import SimulationEvent, EventType
from railway_twin.digital_twin.train import Train

def test_scenario_train_delay_injection(sample_network):
    t1 = Train("T101", "Express Alpha", route=["B1", "B2", "B3"])
    t2 = Train("T102", "Passenger Beta", route=["B1", "B2", "B3"])
    sample_network.register_train(t1)
    sample_network.register_train(t2)

    sim = TrainSimulator(sample_network)
    
    # Schedule 15 minute delay injection for T101 at t=20s
    sim.schedule_event(SimulationEvent(20.0, EventType.DELAY_INJECTION, "T101", {"delay_minutes": 15.0}))

    for _ in range(5):
        sim.step(10.0)

    assert t1.delay_minutes == 15.0
    assert t1.status.value == "DELAYED"
