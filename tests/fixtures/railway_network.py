from railway_twin.digital_twin.network import RailwayNetwork
from railway_twin.digital_twin.block import Block, BlockType
from railway_twin.digital_twin.signal import Signal
from railway_twin.digital_twin.station import Station
from railway_twin.digital_twin.platform import Platform

def create_complex_network() -> RailwayNetwork:
    net = RailwayNetwork("Delhi - Agra Junction Corridor")
    
    # 20 blocks
    for i in range(1, 21):
        b_type = BlockType.MAINLINE if i % 4 != 0 else BlockType.LOOPLINE
        block = Block(f"B{i}", f"Block Segment {i}", length_km=2.5, block_type=b_type)
        net.add_block(block)

    # Connections
    for i in range(1, 20):
        net.connect_blocks(f"B{i}", f"B{i+1}")

    # Stations
    s1 = Station("NDLS", "New Delhi", "NDLS")
    s2 = Station("AGC", "Agra Cantt", "AGC")

    for p in [1, 2, 3]:
        s1.add_platform(Platform(f"NDLS_P{p}", "NDLS", f"Platform {p}"))
        s2.add_platform(Platform(f"AGC_P{p}", "AGC", f"Platform {p}"))

    net.add_station(s1)
    net.add_station(s2)

    # Signals
    for i in range(1, 20):
        net.add_signal(Signal(f"SIG_{i}", f"Signal {i}", target_block_id=f"B{i+1}"))

    return net
