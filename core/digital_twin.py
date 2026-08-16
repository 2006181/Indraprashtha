from core.network import RailwayNetwork
from core.state_manager import StateManager
from core.database_loader import DatabaseLoader
from models.station import Station
from models.train import Train
from models.signal import Signal

class DigitalTwin:
    """
    Main Digital Twin of the Railway Network.
    """
    def __init__(self):
        self.network = RailwayNetwork()
        self.state_manager = StateManager(self.network)

        self.stations = {}
        self.signals = {}

    def load_from_database(self):
        loader = DatabaseLoader()
        data = loader.load()

        for row in data["stations"]:
            station = Station(
                station_id=row["station_code"],
                name=row["station_name"]
            )
            self.add_station(station)

        for row in data["trains"]:
            train = Train(
                train_id=row["train_number"],
                train_type=row["train_type"],
                source=row["source_station"],
                destination=row["destination_station"]
            )


            route_data = data["routes"].get(
                row["train_number"],
                []
            )
            station_route = [
                stop["station_code"]
                for stop in route_data
            ]
            train.set_route(station_route)
            train.start_journey()

            self.state_manager.add_train(train)
        print()
        print(" Digital Twin Loaded Successfully ")
        print(f"Stations : {len(self.stations)}")
        print(f"Trains   : {len(self.state_manager.get_all_trains())}")
        print()

    def add_station(self, station: Station):
        self.stations[station.station_id] = station
        self.network.add_station(station)

    def get_station(self, station_id: str):
        return self.stations.get(station_id)

    def get_all_stations(self):
        return list(self.stations.values())


    def add_signal(self, signal: Signal):
        self.signals[signal.signal_id] = signal

    def get_train(self, train_id: str):
        return self.state_manager.get_train(train_id)

    def get_all_trains(self):
        return self.state_manager.get_all_trains()

    def move_train(self, train_id: str):
        return self.state_manager.move_train(train_id)

    def show_state(self):

        print("\nDIGITAL TWIN ")
        print(f"Stations : {len(self.stations)}")
        print(f"Trains   : {len(self.state_manager.get_all_trains())}")
        print()

        self.network.show_network()
        print()
        self.state_manager.show_state()
