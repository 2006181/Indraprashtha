from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

# ENUMS
class TrainType(str, Enum):
    EXPRESS = "Express"
    FREIGHT = "Freight"
    PASSENGER = "Passenger"


class SignalState(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

# TRAIN
class TrainSchema(BaseModel):
    train_id: str
    train_type: TrainType
    current_block: str
    destination: str

    speed: float = 0.0
    delay: float = 0.0
    priority: int = 1

# BLOCK
class BlockSchema(BaseModel):
    block_id: str

    occupied: bool = False
    occupied_by: Optional[str] = None

# SIGNAL
class SignalSchema(BaseModel):
    signal_id: str
    block_id: str

    state: SignalState = SignalState.RED

# STATION
class StationSchema(BaseModel):
    station_id: str
    name: str

    connected_blocks: List[str] = []

# TEST
if __name__ == "__main__":

    train = TrainSchema(
        train_id="E101",
        train_type=TrainType.EXPRESS,
        current_block="B1",
        destination="Tundla"
    )

    block = BlockSchema(
        block_id="B1"
    )

    signal = SignalSchema(
        signal_id="S1",
        block_id="B1"
    )

    station = StationSchema(
        station_id="ST1",
        name="New Delhi",
        connected_blocks=["B1", "B2"]
    )

    print(train.model_dump())
    print(block.model_dump())
    print(signal.model_dump())
    print(station.model_dump())
