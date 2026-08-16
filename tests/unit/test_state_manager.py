import pytest
from railway_twin.digital_twin.state_manager import StateManager
from railway_twin.digital_twin.train import Train

def test_state_manager_move_train(sample_network):
    sm = StateManager(sample_network)
    t = Train("T101", "Rajdhani")
    sample_network.register_train(t)

    # Move to B1
    res = sm.move_train_to_block("T101", "B1")
    assert res is True
    assert t.current_block_id == "B1"
    assert sample_network.blocks["B1"].state.value == "OCCUPIED"

    # Move to B2 -> release B1, occupy B2
    sm.move_train_to_block("T101", "B2")
    assert t.current_block_id == "B2"
    assert sample_network.blocks["B1"].state.value == "CLEAR"
    assert sample_network.blocks["B2"].state.value == "OCCUPIED"

def test_state_manager_occupancy_conflict(sample_network):
    sm = StateManager(sample_network)
    t1 = Train("T101", "Rajdhani")
    t2 = Train("T102", "Express")
    sample_network.register_train(t1)
    sample_network.register_train(t2)

    sm.move_train_to_block("T101", "B1")
    with pytest.raises(ValueError):
        sm.move_train_to_block("T102", "B1")
