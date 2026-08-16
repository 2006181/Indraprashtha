from enum import Enum
from typing import Optional

class BlockType(Enum):
    MAINLINE = "MAINLINE"
    LOOPLINE = "LOOPLINE"
    CROSSING = "CROSSING"
    STATION = "STATION"

class BlockState(Enum):
    CLEAR = "CLEAR"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    BLOCKED = "BLOCKED"  # Out of service / failed

class Block:
    def __init__(
        self,
        block_id: str,
        name: str,
        length_km: float = 2.0,
        block_type: BlockType = BlockType.MAINLINE,
        max_speed: float = 110.0
    ):
        if not block_id or not isinstance(block_id, str):
            raise ValueError("Invalid block_id")
        if length_km <= 0:
            raise ValueError("Block length must be positive")
            
        self.block_id = block_id
        self.name = name
        self.length_km = length_km
        self.block_type = block_type
        self.max_speed = max_speed
        
        self.state: BlockState = BlockState.CLEAR
        self.occupied_by_train_id: Optional[str] = None
        self.reserved_by_train_id: Optional[str] = None
        self.is_available: bool = True  # Infrastructure status

    def occupy(self, train_id: str) -> bool:
        if not self.is_available or self.state == BlockState.BLOCKED:
            raise ValueError(f"Block {self.block_id} is unavailable/blocked")
        if self.state == BlockState.OCCUPIED and self.occupied_by_train_id != train_id:
            raise ValueError(f"Safety Violation: Block {self.block_id} is already occupied by {self.occupied_by_train_id}")
        
        self.state = BlockState.OCCUPIED
        self.occupied_by_train_id = train_id
        return True

    def release(self, train_id: str) -> bool:
        if self.occupied_by_train_id == train_id:
            self.state = BlockState.CLEAR
            self.occupied_by_train_id = None
            return True
        return False

    def reserve(self, train_id: str) -> bool:
        if self.state == BlockState.CLEAR and self.is_available:
            self.state = BlockState.RESERVED
            self.reserved_by_train_id = train_id
            return True
        return False

    def set_available(self, available: bool):
        self.is_available = available
        if not available:
            self.state = BlockState.BLOCKED

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "name": self.name,
            "length_km": self.length_km,
            "type": self.block_type.value,
            "state": self.state.value,
            "occupied_by": self.occupied_by_train_id,
            "available": self.is_available
        }
