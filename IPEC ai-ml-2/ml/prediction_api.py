import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from ml.schemas import (
    ETARequest, ETAResponse,
    DelayRequest, DelayResponse,
    ConflictRequest, ConflictResponse,
    PredictionAllRequest, PredictionAllResponse,
    DigitalTwinState, HealthResponse, ModelInfoResponse
)
from ml.prediction_service import PredictionService
from ml.digital_twin_adapter import DigitalTwinAdapter
from ml.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SIH25022 — AI/ML Prediction Engine API",
    description="Railway Traffic Control Train ETA, Delay, and Conflict Risk Prediction Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Service Instances
registry = ModelRegistry()
service = PredictionService(registry=registry)
adapter = DigitalTwinAdapter(service=service)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Returns the operational status and loaded state of ML models."""
    return HealthResponse(
        status="OK",
        version="1.0.0",
        models_loaded=registry.load_all_models()
    )


@app.get("/models", response_model=ModelInfoResponse, tags=["Models"])
def get_model_info():
    """Returns metadata, versions, and top 10 important features for all trained models."""
    return ModelInfoResponse(models=registry.get_info())


@app.post("/predict/eta", response_model=ETAResponse, tags=["Predictions"])
def predict_eta(req: ETARequest):
    """Predicts Train ETA / remaining journey duration in minutes."""
    try:
        res = service.predict_eta(
            train_id=req.train_id,
            train_type=req.train_type,
            station_code=req.station_code,
            scheduled_travel_time_mins=req.scheduled_travel_time_mins,
            distance_kms=req.distance_kms,
            historical_avg_delay=req.historical_avg_delay,
            scheduled_departure_hour=req.scheduled_departure_hour,
            day_of_week=req.day_of_week
        )
        return ETAResponse(**res)
    except Exception as e:
        logger.error(f"Error in ETA prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/delay", response_model=DelayResponse, tags=["Predictions"])
def predict_delay(req: DelayRequest):
    """Predicts Train Station Arrival/Departure Delay in minutes."""
    try:
        res = service.predict_delay(
            train_id=req.train_id,
            train_type=req.train_type,
            station_code=req.station_code,
            scheduled_departure_hour=req.scheduled_departure_hour,
            historical_avg_delay=req.historical_avg_delay,
            prev_stop_delay=req.prev_stop_delay,
            day_of_week=req.day_of_week
        )
        return DelayResponse(**res)
    except Exception as e:
        logger.error(f"Error in Delay prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/conflict", response_model=ConflictResponse, tags=["Predictions"])
def predict_conflict(req: ConflictRequest):
    """Predicts Traffic Conflict / Bottleneck Risk Probability between train pairs."""
    try:
        res = service.predict_conflict(
            train_id_a=req.train_id_a,
            train_id_b=req.train_id_b,
            station_code=req.station_code,
            scheduled_gap_mins=req.scheduled_gap_mins,
            time_difference_mins=req.time_difference_mins,
            delay_a=req.delay_a,
            delay_b=req.delay_b,
            train_type_a=req.train_type_a,
            train_type_b=req.train_type_b
        )
        return ConflictResponse(**res)
    except Exception as e:
        logger.error(f"Error in Conflict prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/all", response_model=PredictionAllResponse, tags=["Predictions"])
def predict_all(req: PredictionAllRequest):
    """Executes ETA, Delay, and Conflict predictions in a single request."""
    try:
        res = service.predict_all(
            train_id=req.train_id,
            train_type=req.train_type,
            station_code=req.station_code,
            scheduled_travel_time_mins=req.scheduled_travel_time_mins,
            distance_kms=req.distance_kms,
            historical_avg_delay=req.historical_avg_delay,
            scheduled_departure_hour=req.scheduled_departure_hour,
            day_of_week=req.day_of_week,
            prev_stop_delay=req.prev_stop_delay,
            conflict_check_train_id=req.conflict_check_train_id,
            conflict_scheduled_gap_mins=req.conflict_scheduled_gap_mins
        )
        return PredictionAllResponse(**res)
    except Exception as e:
        logger.error(f"Error in Predict All: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/digital-twin", tags=["Digital Twin Integration"])
def predict_digital_twin(state: DigitalTwinState):
    """Infers predictions directly from Digital Twin state payload for OR-Tools consumption."""
    try:
        return adapter.predict_from_digital_twin_state(state.dict())
    except Exception as e:
        logger.error(f"Error in Digital Twin prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
