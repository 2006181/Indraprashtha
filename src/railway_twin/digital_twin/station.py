from typing import Dict, List, Optional
from .platform import Platform

class Station:
    def __init__(self, station_id: str, name: str, code: str):
        if not station_id or not code:
            raise ValueError("Invalid station parameters")
        self.station_id = station_id
        self.name = name
        self.code = code
        self.platforms: Dict[str, Platform] = {}
        self.connected_blocks: List[str] = []

    def add_platform(self, platform: Platform):
        self.platforms[platform.platform_id] = platform

    def request_platform(self, train_id: str, preferred_platform_id: Optional[str] = None) -> Optional[str]:
        if preferred_platform_id and preferred_platform_id in self.platforms:
            plat = self.platforms[preferred_platform_id]
            if plat.is_available and not plat.is_occupied:
                plat.allocate(train_id)
                return plat.platform_id
        
        # Try to find any free and available platform
        for plat_id, plat in self.platforms.items():
            if plat.is_available and not plat.is_occupied:
                plat.allocate(train_id)
                return plat_id
        return None

    def release_platform(self, platform_id: str, train_id: str) -> bool:
        if platform_id in self.platforms:
            return self.platforms[platform_id].release(train_id)
        return False

    def to_dict(self) -> dict:
        return {
            "station_id": self.station_id,
            "name": self.name,
            "code": self.code,
            "platforms": {pid: p.to_dict() for pid, p in self.platforms.items()}
        }
