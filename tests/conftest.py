import sys
import os
from pathlib import Path
import pytest

# Ensure src/ is on python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from railway_twin.digital_twin.network import RailwayNetwork
from railway_twin.digital_twin.block import Block, BlockType
from railway_twin.digital_twin.signal import Signal, SignalAspect
from railway_twin.digital_twin.station import Station
from railway_twin.digital_twin.platform import Platform
from railway_twin.digital_twin.train import Train, TrainType

@pytest.fixture
def sample_network():
    net = RailwayNetwork("Delhi-Agra Section")

    # Add Blocks B1 to B10
    blocks = []
    for i in range(1, 11):
        b = Block(f"B{i}", f"Block {i}", length_km=2.0, block_type=BlockType.MAINLINE)
        net.add_block(b)
        blocks.append(b)

    # Connect linearly B1 -> B2 -> ... -> B10
    for i in range(len(blocks) - 1):
        net.connect_blocks(blocks[i].block_id, blocks[i+1].block_id)

    # Add Stations & Platforms
    st_a = Station("ST_A", "Station Alpha", "ALPHA")
    st_b = Station("ST_B", "Station Beta", "BETA")
    
    p1 = Platform("P1", "ST_A", "Platform 1")
    p2 = Platform("P2", "ST_A", "Platform 2")
    p3 = Platform("P3", "ST_B", "Platform 1")
    
    st_a.add_platform(p1)
    st_a.add_platform(p2)
    st_b.add_platform(p3)

    net.add_station(st_a)
    net.add_station(st_b)

    # Add Signals S1 to S9 targetting next block
    for i in range(1, 10):
        sig = Signal(f"S{i}", f"Signal {i}", target_block_id=f"B{i+1}")
        net.add_signal(sig)

    return net

@pytest.fixture
def sample_trains():
    t1 = Train("T101", "Rajdhani Express", TrainType.EXPRESS, max_speed=130.0, priority=10, route=["B1", "B2", "B3", "B4", "B5"])
    t2 = Train("T102", "Intercity Passenger", TrainType.PASSENGER, max_speed=110.0, priority=7, route=["B1", "B2", "B3", "B4", "B5"])
    f1 = Train("F201", "Goods Freight", TrainType.FREIGHT, max_speed=75.0, priority=3, route=["B3", "B4", "B5", "B6"])
    return {"T101": t1, "T102": t2, "F201": f1}
