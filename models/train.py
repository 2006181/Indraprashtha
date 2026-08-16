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

        # Current Position
        self.current_station: Optional[str] = None
        self.current_station_index: int = 0

        # Movement
        self.current_block: Optional[str] = None
        self.previous_block: Optional[str] = None
        self.next_block: Optional[str] = None

        # Train Status
        self.speed: float = 0.0
        self.delay: float = 0.0
        self.priority = priority

        # Complete Route
        self.route: List[str] = []

    def set_route(self, route: List[str]):
        self.route = route

    def start_journey(self):
        if self.route:
            self.current_station = self.route[0]
            self.current_station_index = 0

    def move_next_station(self):
        if self.current_station_index < len(self.route) - 1:
            self.current_station_index += 1
            self.current_station = self.route[
                self.current_station_index
            ]
            return True
        return False

    def has_completed_journey(self):
        return (
            self.current_station_index
            >= len(self.route) - 1
        )

    def move_to(self, block_id: str):
        self.previous_block = self.current_block
        self.current_block = block_id
    def set_next_block(self, block_id: str):
        self.next_block = block_id

    def update_speed(self, speed: float):
        self.speed = speed

    def update_delay(self, delay: float):
        self.delay = delay

    def to_dict(self):
        return {
            "train_id": self.train_id,
            "train_type": self.train_type,
            "source": self.source,
            "destination": self.destination,
            "current_station": self.current_station,
            "current_station_index": self.current_station_index,
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
            f"station={self.current_station}, "
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
    )

    train.set_route([
        "NDLS",
        "GZB",
        "ALJN",
        "TDL"
    ])

    train.start_journey()
    print(train)
    while not train.has_completed_journey():
        train.move_next_station()
        print(train.current_station)

    print()
    print(train.to_dict())
