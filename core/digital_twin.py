from core.network import RailwayNetwork
from core.state_manager import StateManager
from models.block import Block
from models.train import Train
from models.station import Station
from models.signal import Signal
class DigitalTwin:
    def __init__(self):
        self.network = RailwayNetwork()
        self.state_manager = StateManager(self.network)
        self.stations = {}
        self.signals = {}

    # Stations
    def add_station(self, station: Station):
        self.stations[station.station_id] = station

    # Signals
    def add_signal(self, signal: Signal):
        self.signals[signal.signal_id] = signal
    
    # Blocks
    def add_block(self, block: Block):
        self.network.add_block(block)

    def connect_blocks(self, block1, block2, distance):
        self.network.connect_blocks(
            block1,
            block2,
            distance
        )

    # Trains
    def add_train(self, train: Train, start_block: str):
        self.state_manager.add_train(
            train,
            start_block
        )

    def move_train(self, train_id, next_block):
        self.state_manager.move_train(
            train_id,
            next_block
        )

    # Dashboard State
    def show_state(self):
        print("\n=========== DIGITAL TWIN ===========")
        self.network.show_network()
        self.state_manager.show_state()

# TEST
if __name__ == "__main__":
    twin = DigitalTwin()
    twin.add_block(Block("B1"))
    twin.add_block(Block("B2"))
    twin.add_block(Block("B3"))
    twin.connect_blocks("B1", "B2", 5)
    twin.connect_blocks("B2", "B3", 6)
    train = Train(
        "E101",
        "Express",
        "New Delhi",
        "Tundla"
    )
    twin.add_train(
        train,
        "B1"
    )
    twin.show_state()
    print("\nMoving Train...\n")
    twin.move_train(
        "E101",
        "B2"
    )
    twin.show_state()
