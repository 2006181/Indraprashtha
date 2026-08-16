import pytest
from railway_twin.digital_twin.network import RailwayNetwork
from railway_twin.digital_twin.block import Block
from railway_twin.digital_twin.train import Train

def test_network_creation(sample_network):
    assert sample_network.section_name == "Delhi-Agra Section"
    assert len(sample_network.blocks) == 10
    assert len(sample_network.stations) == 2
    assert len(sample_network.signals) == 9

def test_duplicate_block_rejection(sample_network):
    b = Block("B1", "Duplicate Block 1")
    with pytest.raises(ValueError):
        sample_network.add_block(b)

def test_invalid_connection(sample_network):
    with pytest.raises(ValueError):
        sample_network.connect_blocks("B1", "INVALID_BLOCK")

def test_route_validation(sample_network):
    valid_route = ["B1", "B2", "B3", "B4"]
    invalid_route = ["B1", "B5", "B2"]
    
    assert sample_network.is_route_valid(valid_route) is True
    assert sample_network.is_route_valid(invalid_route) is False

def test_train_registration_uniqueness(sample_network):
    t1 = Train("T999", "Express A")
    t2 = Train("T999", "Express B")
    
    sample_network.register_train(t1)
    with pytest.raises(ValueError):
        sample_network.register_train(t2)
