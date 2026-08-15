from typing import Dict
from core.network import RailwayNetwork
from models.train import Train
class StateManager:
    """
    Controls the live state of the Digital Twin.
    """

    def __init__(self, network: RailwayNetwork):

        self.network = network

        self.trains: Dict[str, Train] = {}

    # Register Train
    def add_train(
        self,
        train: Train,
        start_block: str
    ):
        block = self.network.get_block(start_block)
        if block is None:
            raise ValueError("Block does not exist.")
        if not block.is_free():
            raise ValueError("Block already occupied.")
        block.occupy(train.train_id)
        train.move_to(start_block)
        self.trains[train.train_id] = train

    # Move Train
    def move_train(
        self,
        train_id: str,
        next_block: str
    ):
        train = self.trains[train_id]
        current = self.network.get_block(
            train.current_block
        )
        target = self.network.get_block(
            next_block
        )
        if target is None:
            raise ValueError("Target block not found.")
        if not target.is_free():
            raise ValueError(
                f"Collision! {next_block} is occupied."
            )
        current.release()
        target.occupy(train_id)
        train.move_to(next_block)

    # Status
    def show_trains(self):
        print("\n========== TRAINS ==========")
        for train in self.trains.values():
            print(train)

    def show_blocks(self):
        print("\n========== BLOCKS ==========")
        for block in self.network.blocks.values():
            print(block)

    def show_state(self):
        self.show_blocks()
        self.show_trains()

# TEST
if __name__ == "__main__":
    from models.block import Block

    # Network
    network = RailwayNetwork()
    network.add_block(Block("B1"))
    network.add_block(Block("B2"))
    network.add_block(Block("B3"))
    network.connect_blocks("B1", "B2")
    network.connect_blocks("B2", "B3")

    # Manager
    manager = StateManager(network)

    # Train
    train = Train(
        train_id="E101",
        train_type="Express",
        source="New Delhi",
        destination="Tundla"
    )
    manager.add_train(
        train,
        "B1"
    )
    manager.show_state()
    print("\nMoving Train...\n")
    manager.move_train(
        "E101",
        "B2"
    )
    manager.show_state()