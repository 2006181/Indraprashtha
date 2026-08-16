import networkx as nx
from models.station import Station

class RailwayNetwork:
    """
    Railway Network Graph using NetworkX.
    Each node represents a railway station.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.stations = {}


    def add_station(self, station: Station):
        self.stations[station.station_id] = station
        self.graph.add_node(
            station.station_id,
            object=station
        )

    def connect_stations(
        self,
        station1: str,
        station2: str,
        distance: float = 1.0
    ):

        self.graph.add_edge(
            station1,
            station2,
            distance=distance
        )


    def get_station(self, station_id: str):
        return self.stations.get(station_id)


    def shortest_route(
        self,
        source: str,
        destination: str
    ):

        return nx.shortest_path(
            self.graph,
            source,
            destination,
            weight="distance"
        )

    def neighbours(self, station_id: str):
        return list(
            self.graph.neighbors(station_id)
        )

    def show_network(self):
        print()
        print("RAILWAY NETWORK")
        print(f"Stations : {len(self.stations)}")
        print(f"Tracks   : {self.graph.number_of_edges()}")
        print()
        print("Sample Connections")
        count = 0
        for u, v, data in self.graph.edges(data=True):
            print(
                f"{u} <------> {v}"
                f" ({data['distance']} km)"
            )
            count += 1
            if count == 10:
                break
