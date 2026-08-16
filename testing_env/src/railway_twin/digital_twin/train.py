from enum import Enum
from typing import Optional, List

class TrainType(Enum):
    EXPRESS = "EXPRESS"
    PASSENGER = "PASSENGER"
    FREIGHT = "FREIGHT"

class TrainStatus(Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    DELAYED = "DELAYED"
    ARRIVED = "ARRIVED"

class Train:
    def __init__(
        self,
        train_id: str,
        name: str,
        train_type: TrainType = TrainType.PASSENGER,
        max_speed: float = 110.0,
        priority: int = 5,
        route: Optional[List[str]] = None
    ):
        if not train_id or not isinstance(train_id, str):
            raise ValueError("Invalid train_id")
        self.train_id = train_id
        self.name = name
        self.train_type = train_type
        self.max_speed = max_speed
        self.priority = priority
        self.current_speed: float = 0.0
        self.position: float = 0.0  # km along section
        self.current_block_id: Optional[str] = None
        self.current_platform_id: Optional[str] = None
        self.route: List[str] = route or []
        self.route_index: int = 0
        self.status: TrainStatus = TrainStatus.SCHEDULED
        self.delay_minutes: float = 0.0
        self.destination_station: Optional[str] = None

    def update_position(self, new_position: float):
        if new_position < 0:
            raise ValueError("Position cannot be negative")
        self.position = new_position

    def update_speed(self, new_speed: float):
        if new_speed < 0:
            raise ValueError("Speed cannot be negative")
        if new_speed > self.max_speed:
            self.current_speed = self.max_speed
        else:
            self.current_speed = new_speed

    def set_current_block(self, block_id: Optional[str]):
        self.current_block_id = block_id

    def update_delay(self, added_delay: float):
        self.delay_minutes = max(0.0, self.delay_minutes + added_delay)
        if self.delay_minutes > 0 and self.status == TrainStatus.RUNNING:
            self.status = TrainStatus.DELAYED

    def get_next_block_id(self) -> Optional[str]:
        if not self.route:
            return None
        if self.current_block_id in self.route:
            idx = self.route.index(self.current_block_id)
            if idx + 1 < len(self.route):
                return self.route[idx + 1]
        elif self.route_index < len(self.route):
            return self.route[self.route_index]
        return None

    def to_dict(self) -> dict:
        return {
            "train_id": self.train_id,
            "name": self.name,
            "train_type": self.train_type.value,
            "speed": self.current_speed,
            "position": self.position,
            "current_block": self.current_block_id,
            "current_platform": self.current_platform_id,
            "delay_minutes": self.delay_minutes,
            "status": self.status.value,
            "priority": self.priority,
            "destination": self.destination_station
        }
