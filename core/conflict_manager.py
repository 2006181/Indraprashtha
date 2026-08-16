from typing import List, Dict
from core.occupancy_manager import OccupancyManager
from core.state_manager import StateManager

class ConflictManager:
    """
    Detects train conflicts in the railway network.
    """
    def __init__(
        self,
        occupancy: OccupancyManager,
        state_manager: StateManager
    ):

        self.occupancy = occupancy
        self.state_manager = state_manager
        self.conflicts: List[Dict] = []

    def detect(self):
        self.conflicts.clear()
        for train in self.state_manager.get_all_trains():
            if train.has_completed_journey():
                continue
            if train.current_station_index >= len(train.route) - 1:
                continue
            next_station = train.route[
                train.current_station_index + 1
            ]
            if not self.occupancy.is_free(next_station):
                occupying_train = self.occupancy.occupied_by(
                    next_station
                )
                if occupying_train != train.train_id:
                    self.conflicts.append({
                        "waiting_train": train.train_id,
                        "occupied_by": occupying_train,
                        "station": next_station
                    })
        return self.conflicts

    def show(self):
        print()
        print("CONFLICTS")
        if not self.conflicts:
            print("No conflicts detected.")
            return

        for conflict in self.conflicts:
            print(
                f"Station : {conflict['station']}"
                f" | Waiting : {conflict['waiting_train']}"
                f" | Occupied : {conflict['occupied_by']}"
            )
        print()
        print(f"Total Conflicts : {len(self.conflicts)}")
