import time
from core.state_manager import StateManager
from core.occupancy_manager import OccupancyManager

class SimulationEngine:
    def __init__(
        self,
        state_manager: StateManager,
        occupancy: OccupancyManager
    ):

        self.state_manager = state_manager
        self.occupancy = occupancy
        self.running = False
        self.tick = 0

    def step(self):
        self.tick += 1
        print(f"\nTICK {self.tick}")
        for train in self.state_manager.get_all_trains()[:10]:
            current = train.current_station
            # Already Finished
            if train.has_completed_journey():
                print(
                    f"{train.train_id} ARRIVED"
                )
                continue
            next_station = train.route[
                train.current_station_index + 1
            ]

            if self.occupancy.is_free(next_station):
                self.occupancy.release(current)
                self.state_manager.move_train(
                    train.train_id
                )
                self.occupancy.occupy(
                    train.current_station,
                    train.train_id
                )
                print(
                    f"{train.train_id} : "
                    f"{current}"
                    f" -> "
                    f"{train.current_station}"
                )
            else:
                print(
                    f"{train.train_id} WAIT "
                    f"({next_station} occupied)"
                )

    def start(
        self,
        delay=1
    ):

        self.running = True
        while self.running:
            self.step()
            time.sleep(delay)

    def stop(self):
        self.running = False
