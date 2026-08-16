import pytest
from railway_twin.simulation.telemetry import TelemetryGenerator
from railway_twin.digital_twin.train import Train

def test_telemetry_generation_and_consistency(sample_network):
    t = Train("T101", "Express")
    t.position = 5.2
    t.update_speed(80.0)
    t.set_current_block("B2")
    sample_network.register_train(t)

    gen = TelemetryGenerator(sample_network)
    frame = gen.capture_frame(timestamp=100.0, train_id="T101")

    assert frame.train_id == "T101"
    assert frame.position_km == 5.2
    assert frame.speed_kmh == 80.0
    assert frame.current_block_id == "B2"
    assert gen.is_consistent_with_twin(frame) is True
