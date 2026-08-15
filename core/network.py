import networkx as nx
from models.block import Block
class RailwayNetwork:
    """
    Railway Graph using NetworkX
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.blocks = {}
        
    # Blocks
    def add_block(self, block: Block):
        self.blocks[block.block_id] = block
        self.graph.add_node(
            block.block_id,
            object=block
        )
 
    # Tracks
    def connect_blocks(
        self,
        block1: str,
        block2: str,
        distance: float = 1.0
    ):

        self.graph.add_edge(
            block1,
            block2,
            distance=distance
        )

    # Get Block
    def get_block(self, block_id: str):
        return self.blocks.get(block_id)

    # Route
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

    # Neighbours
    def neighbours(self, block_id: str):
        return list(
            self.graph.neighbors(block_id)
        )

    # Status
    def show_network(self):
        print("\n========== BLOCKS ==========")
        for block in self.blocks.values():
            print(block)
        print("\n========== TRACKS ==========")
        for u, v, data in self.graph.edges(data=True):
            print(
                f"{u} <------> {v} "
                f"({data['distance']} km)"
            )

# TEST
if __name__ == "__main__":
    railway = RailwayNetwork()
    b1 = Block("B1")
    b2 = Block("B2")
    b3 = Block("B3")
    b4 = Block("B4")
    railway.add_block(b1)
    railway.add_block(b2)
    railway.add_block(b3)
    railway.add_block(b4)
    railway.connect_blocks("B1", "B2", 5)
    railway.connect_blocks("B2", "B3", 7)
    railway.connect_blocks("B3", "B4", 4)
    railway.show_network()
    print("\nShortest Route")
    print(
        railway.shortest_route(
            "B1",
            "B4"
        )
    )
    print("\nNeighbours of B2")
    print(
        railway.neighbours("B2")
    )