from typing import Optional
class Block:
    """
    Represents a railway block.
    A block can be occupied by only one train at a time.
    """
    def __init__(
        self,
        block_id: str,
        length: float = 1.0,
        speed_limit: float = 100.0
    ):

        self.block_id = block_id
        self.length = length
        self.speed_limit = speed_limit

        self.occupied = False
        self.train_id: Optional[str] = None

        self.signal_id: Optional[str] = None

    # Occupancy
    def occupy(self, train_id: str):

        if self.occupied:
            raise ValueError(
                f"Block {self.block_id} already occupied by {self.train_id}"
            )

        self.occupied = True
        self.train_id = train_id

    def release(self):

        self.occupied = False
        self.train_id = None

    # Signal
    def assign_signal(self, signal_id: str):

        self.signal_id = signal_id

    # Status
    def is_free(self):
        return not self.occupied
    def to_dict(self):
        return {
            "block_id": self.block_id,
            "length": self.length,
            "speed_limit": self.speed_limit,
            "occupied": self.occupied,
            "train_id": self.train_id,
            "signal_id": self.signal_id,
        }
    def __repr__(self):
        status = "Occupied" if self.occupied else "Free"
        return (
            f"Block("
            f"id={self.block_id}, "
            f"status={status}, "
            f"train={self.train_id}"
            f")"
        )
    
# TEST
if __name__ == "__main__":

    block = Block(
        block_id="B1",
        length=2.5,
        speed_limit=80
    )
    print(block)
    block.occupy("E101")
    print(block)
    block.release()
    print(block)
