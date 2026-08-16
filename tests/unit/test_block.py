import pytest
from railway_twin.digital_twin.block import Block, BlockState, BlockType

def test_block_initialization():
    b = Block("B1", "Mainline Block 1", length_km=2.5)
    assert b.block_id == "B1"
    assert b.state == BlockState.CLEAR
    assert b.is_available is True

def test_block_occupancy_valid():
    b = Block("B1", "Mainline Block 1")
    res = b.occupy("T101")
    assert res is True
    assert b.state == BlockState.OCCUPIED
    assert b.occupied_by_train_id == "T101"

def test_block_single_occupancy_violation():
    b = Block("B1", "Mainline Block 1")
    b.occupy("T101")
    
    # Second train occupying occupied block must raise error
    with pytest.raises(ValueError, match="Safety Violation"):
        b.occupy("T102")

def test_block_release():
    b = Block("B1", "Mainline Block 1")
    b.occupy("T101")
    res = b.release("T101")
    assert res is True
    assert b.state == BlockState.CLEAR
    assert b.occupied_by_train_id is None

def test_unavailable_block_occupancy():
    b = Block("B1", "Mainline Block 1")
    b.set_available(False)
    assert b.state == BlockState.BLOCKED
    with pytest.raises(ValueError):
        b.occupy("T101")
