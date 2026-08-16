from railway_twin.simulation.events import SimulationEvent, EventType

def test_simulation_event_priority():
    ev1 = SimulationEvent(100.0, EventType.DELAY_INJECTION, "T101")
    ev2 = SimulationEvent(50.0, EventType.BLOCK_FAILURE, "B5")

    assert ev2 < ev1
