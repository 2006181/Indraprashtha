from typing import Dict, Optional

class OccupancyManager:
    """
    Keeps track of which train occupies which station.
    """
    def __init__(self):
        self.station_occupancy: Dict[str, Optional[str]] = {}

    def initialize(self, stations):
        for station in stations:
            self.station_occupancy[station.station_id] = None

    def occupy(self, station_id: str, train_id: str):
        self.station_occupancy[station_id] = train_id

    def release(self, station_id: str):
        self.station_occupancy[station_id] = None

    def is_free(self, station_id: str):
        return self.station_occupancy.get(station_id) is None

    def occupied_by(self, station_id: str):
        return self.station_occupancy.get(station_id)

    def show(self):
        print("OCCUPANCY")
        occupied = 0
        for station, train in self.station_occupancy.items():
            if train is not None:
                occupied += 1
                print(f"{station} -> {train}")
        print()
        print(f"Occupied Stations : {occupied}")
