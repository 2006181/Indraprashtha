import pytest
from railway_twin.digital_twin.signal import Signal, SignalAspect

def test_signal_aspect_transitions():
    s = Signal("S1", "Signal 1", target_block_id="B2")
    assert s.aspect == SignalAspect.RED

    s.update_aspect_from_block_state("CLEAR", "CLEAR")
    assert s.aspect == SignalAspect.GREEN

    s.update_aspect_from_block_state("CLEAR", "OCCUPIED")
    assert s.aspect == SignalAspect.YELLOW

    s.update_aspect_from_block_state("OCCUPIED", "CLEAR")
    assert s.aspect == SignalAspect.RED

def test_failed_signal():
    s = Signal("S1", "Signal 1", target_block_id="B2")
    s.set_functional(False)
    assert s.aspect == SignalAspect.RED

    with pytest.raises(ValueError):
        s.set_aspect(SignalAspect.GREEN)
