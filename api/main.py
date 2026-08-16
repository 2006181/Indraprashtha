from fastapi import FastAPI
from core.digital_twin import DigitalTwin
from core.occupancy_manager import OccupancyManager
from core.conflict_manager import ConflictManager
from core.simulation_engine import SimulationEngine

app = FastAPI(
    title="Railway Digital Twin",
    version="1.0"
)

# Load Everything Once
twin = DigitalTwin()
twin.load_from_database()

occupancy = OccupancyManager()
occupancy.initialize(
    twin.get_all_stations()
)
for train in twin.get_all_trains():
    occupancy.occupy(
        train.current_station,
        train.train_id
    )

simulation = SimulationEngine(
    twin.state_manager,
    occupancy
)

conflict_manager = ConflictManager(
    occupancy,
    twin.state_manager
)

# APIs
@app.get("/")
def home():
    return {
        "message": "Railway Digital Twin Running"
    }

@app.get("/stats")
def stats():
    conflicts = conflict_manager.detect()
    occupied = sum(
        1
        for value in occupancy.station_occupancy.values()
        if value is not None
    )

    return {

        "stations": len(
            twin.get_all_stations()
        ),

        "trains": len(
            twin.get_all_trains()
        ),
        "occupied_stations": occupied,
        "conflicts": len(conflicts)
    }

@app.get("/trains")
def trains():
    return [
        train.to_dict()
        for train in twin.get_all_trains()
    ]

@app.get("/conflicts")
def conflicts():
    return conflict_manager.detect()

@app.get("/simulation/step")
def simulation_step():
    simulation.step()
    conflicts = conflict_manager.detect()
    return {
        "tick": simulation.tick,
        "conflicts": len(conflicts)
    }
