import pytest
from railway_twin.digital_twin.train import Train, TrainType, TrainStatus

def test_train_initialization():
    t = Train("T101", "Shatabdi", TrainType.EXPRESS, max_speed=130.0, priority=10)
    assert t.train_id == "T101"
    assert t.max_speed == 130.0
    assert t.status == TrainStatus.SCHEDULED
    assert t.delay_minutes == 0.0

def test_invalid_train_id():
    with pytest.raises(ValueError):
        Train("", "Invalid")

def test_position_and_speed_updates():
    t = Train("T101", "Shatabdi")
    t.update_position(12.5)
    assert t.position == 12.5

    with pytest.raises(ValueError):
        t.update_position(-5.0)

    t.update_speed(90.0)
    assert t.current_speed == 90.0

    t.update_speed(200.0)  # Max capped at max_speed (110 default)
    assert t.current_speed == 110.0

    with pytest.raises(ValueError):
        t.update_speed(-10.0)

def test_delay_updates():
    t = Train("T101", "Shatabdi")
    t.status = TrainStatus.RUNNING
    t.update_delay(15.0)
    assert t.delay_minutes == 15.0
    assert t.status == TrainStatus.DELAYED

def test_train_to_dict():
    t = Train("T101", "Shatabdi")
    d = t.to_dict()
    assert d["train_id"] == "T101"
    assert d["status"] == "SCHEDULED"
