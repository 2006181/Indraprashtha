from enum import Enum
from typing import Optional

class SignalAspect(Enum):
    RED = "RED"          # Stop
    YELLOW = "YELLOW"    # Proceed with caution / expect red at next signal
    GREEN = "GREEN"      # Clear / Proceed at full speed

class Signal:
    def __init__(
        self,
        signal_id: str,
        name: str,
        target_block_id: str
    ):
        if not signal_id:
            raise ValueError("Invalid signal_id")
        self.signal_id = signal_id
        self.name = name
        self.target_block_id = target_block_id
        self.aspect: SignalAspect = SignalAspect.RED
        self.is_functional: bool = True

    def set_aspect(self, new_aspect: SignalAspect):
        if not self.is_functional and new_aspect != SignalAspect.RED:
            raise ValueError(f"Signal {self.signal_id} is failed and must remain RED")
        self.aspect = new_aspect

    def update_aspect_from_block_state(self, block_state_str: str, next_block_state_str: Optional[str] = None):
        if not self.is_functional:
            self.aspect = SignalAspect.RED
            return

        if block_state_str in ("OCCUPIED", "BLOCKED"):
            self.aspect = SignalAspect.RED
        elif next_block_state_str in ("OCCUPIED", "BLOCKED"):
            self.aspect = SignalAspect.YELLOW
        else:
            self.aspect = SignalAspect.GREEN

    def set_functional(self, functional: bool):
        self.is_functional = functional
        if not functional:
            self.aspect = SignalAspect.RED

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "name": self.name,
            "target_block_id": self.target_block_id,
            "aspect": self.aspect.value,
            "functional": self.is_functional
        }
