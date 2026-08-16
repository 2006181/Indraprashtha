from dataclasses import dataclass
from typing import Dict, List, Optional
from ..digital_twin.network import RailwayNetwork

@dataclass
class TelemetryFrame:
    timestamp: float
    train_id: str
    position_km: float
    speed_kmh: float
    current_block_id: Optional[str]
    delay_minutes: float

class TelemetryGenerator:
    def __init__(self, network: RailwayNetwork):
        self.network = network

    def capture_frame(self, timestamp: float, train_id: str) -> TelemetryFrame:
        if train_id not in self.network.trains:
            raise KeyError(f"Train {train_id} not in network")
        t = self.network.trains[train_id]
        return TelemetryFrame(
            timestamp=timestamp,
            train_id=t.train_id,
            position_km=t.position,
            speed_kmh=t.current_speed,
            current_block_id=t.current_block_id,
            delay_minutes=t.delay_minutes
        )

    def is_consistent_with_twin(self, frame: TelemetryFrame) -> bool:
        if frame.train_id not in self.network.trains:
            return False
        t = self.network.trains[frame.train_id]
        return (
            t.current_block_id == frame.current_block_id and
            abs(t.position - frame.position_km) < 1e-3 and
            abs(t.current_speed - frame.speed_kmh) < 1e-3
        )
