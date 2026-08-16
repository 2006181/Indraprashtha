from database.train_repository import TrainRepository
from database.station_repository import StationRepository
from database.route_repository import RouteRepository

class DatabaseLoader:
    """
    Loads all required data from the MySQL database.
    """
    def __init__(self):
        self.trains = []
        self.stations = []
        self.routes = {}

    def load(self):
        print("Loading trains...")
        self.trains = TrainRepository.get_all_trains()

        print("Loading stations...")
        self.stations = StationRepository.get_all_stations()

        print("Loading routes...")
        all_routes = RouteRepository.get_all_routes()
        self.routes = {}
        for route in all_routes:
            train_number = route["train_number"]
            if train_number not in self.routes:
                self.routes[train_number] = []
            self.routes[train_number].append(route)

        print()
        print("DATABASE LOADED")
        print(f"Total Trains   : {len(self.trains)}")
        print(f"Total Stations : {len(self.stations)}")
        print(f"Total Routes   : {len(self.routes)}")

        return {
            "trains": self.trains,
            "stations": self.stations,
            "routes": self.routes
        }
