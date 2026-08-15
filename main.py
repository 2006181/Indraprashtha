from fastapi import FastAPI, HTTPException
from core.digital_twin import DigitalTwin
from models.block import Block
from models.train import Train
app = FastAPI(title="Railway Digital Twin API")

# Create Digital Twin
twin = DigitalTwin()

# Sample Railway Network
twin.add_block(Block("B1"))
twin.add_block(Block("B2"))
twin.add_block(Block("B3"))
twin.add_block(Block("B4"))
twin.connect_blocks("B1", "B2", 5)
twin.connect_blocks("B2", "B3", 7)
twin.connect_blocks("B3", "B4", 4)

# Sample Train
train = Train(
    train_id="E101",
    train_type="Express",
    source="New Delhi",
    destination="Tundla"
)
twin.add_train(train, "B1")

# APIs
@app.get("/")
def home():
    return {"message": "Railway Digital Twin Running 🚆"}

@app.get("/blocks")
def get_blocks():
    return [
        block.to_dict()
        for block in twin.network.blocks.values()
    ]

@app.get("/trains")
def get_trains():
    return [
        train.to_dict()
        for train in twin.state_manager.trains.values()
    ]

@app.get("/network")
def get_network():
    return {
        "nodes": list(twin.network.graph.nodes),
        "edges": list(twin.network.graph.edges)
    }

@app.post("/move_train/{train_id}/{block_id}")
def move_train(train_id: str, block_id: str):
    try:
        twin.move_train(
            train_id,
            block_id
        )
        return {
            "message": f"{train_id} moved to {block_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@app.get("/state")
def get_state():
    return {
        "blocks": [
            b.to_dict()
            for b in twin.network.blocks.values()
        ],
        "trains": [
            t.to_dict()
            for t in twin.state_manager.trains.values()
        ]
    }
