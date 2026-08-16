from typing import Dict
from models.train import Train
from core.network import RailwayNetwork

class StateManager:
    """
    Controls the runtime state of all trains.
    """
    def __init__(self, network: RailwayNetwork):
        self.network = network
        self.trains: Dict[str, Train] = {}

    def add_train(self, train: Train):
        self.trains[train.train_id] = train

    def get_train(self, train_id: str):
        return self.trains.get(train_id)

    def get_all_trains(self):
        return list(self.trains.values())

    def move_train(self, train_id: str):
        train = self.get_train(train_id)
        if train is None:
            raise ValueError("Train not found.")
        moved = train.move_next_station()
        return moved

    def show_trains(self):
        print("\nTRAINS")
        for train in self.trains.values():
            print(
                f"{train.train_id}"
                f" | {train.current_station}"
                f" | Delay: {train.delay}"
                f" | Speed: {train.speed}"
            )

    def show_state(self):
        self.show_trains()
