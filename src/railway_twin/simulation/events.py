from enum import Enum
from typing import Dict, Any, Optional

class EventType(Enum):
    DELAY_INJECTION = "DELAY_INJECTION"
    BLOCK_FAILURE = "BLOCK_FAILURE"
    SIGNAL_FAILURE = "SIGNAL_FAILURE"
    PLATFORM_FAILURE = "PLATFORM_FAILURE"
    TRAIN_DEPARTURE = "TRAIN_DEPARTURE"
    TRAIN_ARRIVAL = "TRAIN_ARRIVAL"
    SPEED_CHANGE = "SPEED_CHANGE"

class SimulationEvent:
    def __init__(
        self,
        event_time_seconds: float,
        event_type: EventType,
        target_id: str,
        payload: Optional[Dict[str, Any]] = None
    ):
        self.event_time_seconds = event_time_seconds
        self.event_type = event_type
        self.target_id = target_id
        self.payload = payload or {}

    def __lt__(self, other: "SimulationEvent"):
        return self.event_time_seconds < other.event_time_seconds
