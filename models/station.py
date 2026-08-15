from typing import List
class Station:
    """
    Represents a railway station.
    """
    def __init__(
        self,
        station_id: str,
        name: str
    ):

        self.station_id = station_id
        self.name = name

        self.blocks: List[str] = []

    # Blocks
    def add_block(self, block_id: str):
        if block_id not in self.blocks:
            self.blocks.append(block_id)

    def remove_block(self, block_id: str):
        if block_id in self.blocks:
            self.blocks.remove(block_id)

    # Export
    def to_dict(self):
        return {
            "station_id": self.station_id,
            "name": self.name,
            "blocks": self.blocks
        }

    def __repr__(self):
        return (
            f"Station("
            f"id={self.station_id}, "
            f"name={self.name}, "
            f"blocks={self.blocks}"
            f")"
        )

# TEST
if __name__ == "__main__":
    station = Station(
        "ST1",
        "New Delhi"
    )
    station.add_block("B1")
    station.add_block("B2")
    print(station)
    print(station.to_dict())
