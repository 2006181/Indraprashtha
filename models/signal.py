from enum import Enum
class SignalState(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

class Signal:
    """
    Represents a railway signal.
    """
    def __init__(self, signal_id: str, block_id: str):
        self.signal_id = signal_id
        self.block_id = block_id
        self.state = SignalState.RED
        
    # State Updates
    def set_red(self):
        self.state = SignalState.RED

    def set_yellow(self):
        self.state = SignalState.YELLOW

    def set_green(self):
        self.state = SignalState.GREEN


    # Export
    def to_dict(self):
        return {
            "signal_id": self.signal_id,
            "block_id": self.block_id,
            "state": self.state.value
        }

    def __repr__(self):
        return (
            f"Signal("
            f"id={self.signal_id}, "
            f"block={self.block_id}, "
            f"state={self.state.value}"
            f")"
        )

# TEST
if __name__ == "__main__":
    signal = Signal("S1", "B1")
    print(signal)
    signal.set_green()
    print(signal)
    signal.set_yellow()
    print(signal)
    signal.set_red()
    print(signal)
