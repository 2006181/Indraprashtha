from typing import List, Optional
class Train:
    """
    Represents a train in the railway network.
    """
    def __init__(
        self,
        train_id: str,
        train_type: str,
        source: str,
        destination: str,
        priority: int = 1,
    ):
        self.train_id = train_id
        self.train_type = train_type

        self.source = source
        self.destination = destination

        self.current_block: Optional[str] = None
        self.previous_block: Optional[str] = None
        self.next_block: Optional[str] = None

        self.speed: float = 0.0
        self.delay: float = 0.0
        self.priority = priority

        self.route: List[str] = []

    # Route
    def set_route(self, route: List[str]):
        self.route = route

    # Movement
    def move_to(self, block_id: str):
        self.previous_block = self.current_block
        self.current_block = block_id
    def set_next_block(self, block_id: str):
        self.next_block = block_id

    # Speed
    def update_speed(self, speed: float):
        self.speed = speed

    # Delay
    def update_delay(self, delay: float):
        self.delay = delay

    # Export
    def to_dict(self):
        return {
            "train_id": self.train_id,
            "train_type": self.train_type,
            "source": self.source,
            "destination": self.destination,
            "current_block": self.current_block,
            "previous_block": self.previous_block,
            "next_block": self.next_block,
            "speed": self.speed,
            "delay": self.delay,
            "priority": self.priority,
            "route": self.route,
        }
    def __repr__(self):
        return (
            f"Train("
            f"id={self.train_id}, "
            f"block={self.current_block}, "
            f"speed={self.speed} km/h, "
            f"delay={self.delay} min)"
        )

# TEST
if __name__ == "__main__":
    train = Train(
        train_id="E101",
        train_type="Express",
        source="New Delhi",
        destination="Tundla",
        priority=1,
    )
    train.set_route(["B1", "B2", "B3"])
    train.move_to("B1")
    train.set_next_block("B2")
    train.update_speed(82)
    train.update_delay(2)
    print(train)
    print(train.to_dict())