from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    DelayPredictionRequest,
    ScenarioRequest,
    StepRequest,
    OptimizationRequest,
    TrainCreate,
)
from .twin import DigitalTwin
from .ml import train_model, predict_for_train, ensure_model
from .optimizer import optimize_sequence
from .simulation import run_scenario

app = FastAPI(
    title="SIH25022 Railway Digital Twin Backend",
    version="1.0.0",
    description=(
        "AI-assisted railway traffic simulation, delay prediction and "
        "conflict-aware train sequencing prototype."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

twin = DigitalTwin()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "sih25022-backend",
        "clock_minute": twin.clock_minute,
    }


@app.get("/network")
def network():
    return twin.network.to_dict()


@app.get("/trains")
def trains():
    return [t.model_dump() for t in twin.trains.values()]


@app.get("/state")
def state():
    return twin.state()


@app.get("/metrics")
def metrics():
    return twin.metrics()


@app.post("/simulation/reset")
def reset_simulation():
    twin.reset()
    return twin.state()


@app.post("/simulation/step")
def step_simulation(req: StepRequest):
    return twin.step(req.minutes)


@app.post("/simulation/add-train")
def add_train(req: TrainCreate):
    if req.train_id in twin.trains:
        raise HTTPException(status_code=409, detail="Train already exists.")

    from .schemas import Train

    train = Train(
        train_id=req.train_id,
        train_type=req.train_type,
        priority=req.priority,
        origin=req.origin,
        destination=req.destination,
        current_block=req.start_block,
        next_block=twin.network.next_block(req.start_block),
        speed_kmph=req.speed_kmph,
        max_speed_kmph=req.max_speed_kmph,
        scheduled_arrival_min=req.scheduled_arrival_min,
        scheduled_departure_min=req.scheduled_departure_min,
        current_delay_min=0,
        distance_to_station_km=twin.network.blocks[req.start_block].length_km,
    )
    twin.add_train(train)
    return train.model_dump()


@app.post("/ml/train")
def ml_train():
    return train_model()


@app.post("/ml/predict-delay")
def ml_predict(req: DelayPredictionRequest):
    train = twin.trains.get(req.train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found.")
    return predict_for_train(train, twin)


@app.post("/simulation/scenario")
def scenario(req: ScenarioRequest):
    if req.train_id not in twin.trains:
        raise HTTPException(status_code=404, detail="Train not found.")
    try:
        return run_scenario(
            twin,
            req.train_id,
            req.delay_minutes,
            req.horizon_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/optimization/sequence")
def optimization(req: OptimizationRequest):
    return optimize_sequence(
        twin,
        req.block_id,
        req.horizon_minutes,
    )


@app.post("/optimization/recommend")
def recommend(req: OptimizationRequest):
    result = optimize_sequence(
        twin,
        req.block_id,
        req.horizon_minutes,
    )

    if not result["ordered_train_ids"]:
        result["recommended_action"] = "NO_ACTION"
        return result

    first = result["ordered_train_ids"][0]
    train = twin.trains[first]

    result["recommended_action"] = {
        "type": "PRIORITIZE_TRAIN",
        "train_id": first,
        "reason": (
            f"Train {first} is selected first because its priority="
            f"{train.priority} and current delay={train.current_delay_min:.1f} min."
        ),
        "safety_note": (
            "This is decision support only. A real deployment requires "
            "formal railway signalling/safety validation."
        ),
    }
    return result


@app.on_event("startup")
def startup():
    # Do not train a model during every import if it already exists.
    ensure_model()