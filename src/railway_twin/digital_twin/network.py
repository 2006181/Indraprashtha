from typing import Dict, List, Optional
from .block import Block, BlockState
from .signal import Signal, SignalAspect
from .station import Station
from .train import Train

class RailwayNetwork:
    def __init__(self, section_name: str = "Main Corridor Section"):
        self.section_name = section_name
        self.blocks: Dict[str, Block] = {}
        self.signals: Dict[str, Signal] = {}
        self.stations: Dict[str, Station] = {}
        self.trains: Dict[str, Train] = {}
        self.adjacency: Dict[str, List[str]] = {}  # Block graph connections

    def add_block(self, block: Block):
        if block.block_id in self.blocks:
            raise ValueError(f"Block ID {block.block_id} already exists")
        self.blocks[block.block_id] = block
        if block.block_id not in self.adjacency:
            self.adjacency[block.block_id] = []

    def connect_blocks(self, from_block_id: str, to_block_id: str):
        if from_block_id not in self.blocks or to_block_id not in self.blocks:
            raise ValueError("Both blocks must exist in network before connecting")
        if to_block_id not in self.adjacency[from_block_id]:
            self.adjacency[from_block_id].append(to_block_id)

    def add_signal(self, signal: Signal):
        self.signals[signal.signal_id] = signal

    def add_station(self, station: Station):
        self.stations[station.station_id] = station

    def register_train(self, train: Train):
        if train.train_id in self.trains:
            raise ValueError(f"Train ID {train.train_id} is not unique!")
        self.trains[train.train_id] = train

    def update_all_signals(self):
        for sig in self.signals.values():
            target_block = self.blocks.get(sig.target_block_id)
            if not target_block:
                continue
            next_blocks = self.adjacency.get(sig.target_block_id, [])
            next_block_state = None
            if next_blocks and next_blocks[0] in self.blocks:
                next_block_state = self.blocks[next_blocks[0]].state.value
            
            sig.update_aspect_from_block_state(
                target_block.state.value,
                next_block_state
            )

    def is_route_valid(self, block_sequence: List[str]) -> bool:
        if not block_sequence:
            return False
        for i in range(len(block_sequence) - 1):
            curr = block_sequence[i]
            nxt = block_sequence[i + 1]
            if curr not in self.blocks or nxt not in self.blocks:
                return False
            if nxt not in self.adjacency.get(curr, []):
                return False
            if not self.blocks[nxt].is_available:
                return False
        return True

    def to_dict(self) -> dict:
        return {
            "section_name": self.section_name,
            "blocks": {bid: b.to_dict() for bid, b in self.blocks.items()},
            "signals": {sid: s.to_dict() for sid, s in self.signals.items()},
            "stations": {st_id: st.to_dict() for st_id, st in self.stations.items()},
            "trains": {tid: t.to_dict() for tid, t in self.trains.items()}
        }
