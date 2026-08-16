from typing import Optional

class Platform:
    def __init__(
        self,
        platform_id: str,
        station_id: str,
        name: str,
        length_meters: float = 600.0
    ):
        if not platform_id or not station_id:
            raise ValueError("Invalid platform_id or station_id")
        self.platform_id = platform_id
        self.station_id = station_id
        self.name = name
        self.length_meters = length_meters
        
        self.occupied_by_train_id: Optional[str] = None
        self.is_available: bool = True

    @property
    def is_occupied(self) -> bool:
        return self.occupied_by_train_id is not None

    def allocate(self, train_id: str) -> bool:
        if not self.is_available:
            raise ValueError(f"Platform {self.platform_id} is out of service")
        if self.is_occupied and self.occupied_by_train_id != train_id:
            raise ValueError(f"Platform {self.platform_id} already occupied by train {self.occupied_by_train_id}")
        self.occupied_by_train_id = train_id
        return True

    def release(self, train_id: str) -> bool:
        if self.occupied_by_train_id == train_id:
            self.occupied_by_train_id = None
            return True
        return False

    def set_available(self, available: bool):
        self.is_available = available

    def to_dict(self) -> dict:
        return {
            "platform_id": self.platform_id,
            "station_id": self.station_id,
            "name": self.name,
            "occupied_by": self.occupied_by_train_id,
            "available": self.is_available
        }
