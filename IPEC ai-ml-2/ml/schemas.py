from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ETARequest(BaseModel):
    train_id: str = Field(..., json_schema_extra={"example": "12673"}, description="Train Number or ID")
    train_type: str = Field("Express", json_schema_extra={"example": "Express"}, description="Train Type: Express, Passenger, Superfast")
    station_code: str = Field(..., json_schema_extra={"example": "CBE"}, description="Destination or Target Station Code")
    scheduled_travel_time_mins: Optional[float] = Field(None, json_schema_extra={"example": 420.0}, description="Scheduled travel time in minutes")
    distance_kms: Optional[float] = Field(None, json_schema_extra={"example": 492.0}, description="Distance in kms")
    historical_avg_delay: Optional[float] = Field(None, json_schema_extra={"example": 15.5}, description="Historical average delay for train/station")
    scheduled_departure_hour: Optional[int] = Field(None, ge=0, le=23, json_schema_extra={"example": 22}, description="Departure hour (0-23)")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, json_schema_extra={"example": 1}, description="Day of week (0=Mon, 6=Sun)")


class ETAResponse(BaseModel):
    train_id: str
    predicted_eta_minutes: float
    unit: str = "minutes"
    model_version: str = "1.0.0"


class DownstreamStopDelay(BaseModel):
    station_code: str
    station_name: str
    scheduled_arrival: str
    predicted_delay_minutes: float


class DelayRequest(BaseModel):
    train_id: str = Field(..., json_schema_extra={"example": "12673"}, description="Train Number or ID")
    train_type: str = Field("Express", json_schema_extra={"example": "Express"}, description="Train Type")
    station_code: str = Field(..., json_schema_extra={"example": "MAS"}, description="Current or target station code")
    scheduled_departure_hour: Optional[int] = Field(None, ge=0, le=23, json_schema_extra={"example": 18})
    historical_avg_delay: Optional[float] = Field(None, json_schema_extra={"example": 24.0})
    prev_stop_delay: Optional[float] = Field(0.0, json_schema_extra={"example": 10.0})
    day_of_week: Optional[int] = Field(None, ge=0, le=6, json_schema_extra={"example": 2})


class DelayResponse(BaseModel):
    train_id: str
    predicted_delay_minutes: float
    downstream_propagation: Optional[List[DownstreamStopDelay]] = None
    model_version: str = "1.0.0"


class ConflictRequest(BaseModel):
    train_id_a: str = Field(..., json_schema_extra={"example": "12673"})
    train_id_b: str = Field(..., json_schema_extra={"example": "12674"})
    station_code: str = Field(..., json_schema_extra={"example": "MAS"})
    scheduled_gap_mins: float = Field(..., json_schema_extra={"example": 5.0}, description="Scheduled gap between train departures/arrivals")
    time_difference_mins: float = Field(..., json_schema_extra={"example": 8.0}, description="Time gap between expected arrivals")
    delay_a: float = Field(0.0, json_schema_extra={"example": 15.0}, description="Current delay of Train A in minutes")
    delay_b: float = Field(0.0, json_schema_extra={"example": 2.0}, description="Current delay of Train B in minutes")
    train_type_a: str = Field("Express", json_schema_extra={"example": "Express"})
    train_type_b: str = Field("Superfast", json_schema_extra={"example": "Superfast"})


class ConflictResponse(BaseModel):
    train_id_a: str
    train_id_b: str
    station_code: str
    conflict_probability: float
    risk_level: str = Field(..., json_schema_extra={"example": "CRITICAL"}, description="LOW, MEDIUM, HIGH, CRITICAL")
    method: str = Field("ml", json_schema_extra={"example": "ml"}, description="ml or schedule_based")


class PredictionAllRequest(BaseModel):
    train_id: str = Field(..., json_schema_extra={"example": "12673"})
    train_type: str = Field("Express", json_schema_extra={"example": "Express"})
    station_code: str = Field(..., json_schema_extra={"example": "CBE"})
    scheduled_travel_time_mins: Optional[float] = Field(None, json_schema_extra={"example": 420.0})
    distance_kms: Optional[float] = Field(None, json_schema_extra={"example": 492.0})
    historical_avg_delay: Optional[float] = Field(None, json_schema_extra={"example": 15.5})
    scheduled_departure_hour: Optional[int] = Field(None, ge=0, le=23, json_schema_extra={"example": 22})
    day_of_week: Optional[int] = Field(None, ge=0, le=6, json_schema_extra={"example": 1})
    prev_stop_delay: Optional[float] = Field(0.0, json_schema_extra={"example": 5.0})
    conflict_check_train_id: Optional[str] = Field(None, json_schema_extra={"example": "12674"})
    conflict_scheduled_gap_mins: Optional[float] = Field(10.0, json_schema_extra={"example": 10.0})


class PredictionAllResponse(BaseModel):
    train_id: str
    station_code: str
    eta: ETAResponse
    delay: DelayResponse
    conflict: Optional[ConflictResponse] = None
    optimizer_payload: Dict[str, Any]


class DigitalTwinTrainState(BaseModel):
    train_id: str
    train_type: str = "Express"
    station_code: str
    delay_minutes: float = 0.0
    speed_kmh: Optional[float] = None
    scheduled_departure_hour: Optional[int] = None
    scheduled_travel_time_mins: Optional[float] = None
    distance_kms: Optional[float] = None


class DigitalTwinState(BaseModel):
    timestamp: str
    trains: List[DigitalTwinTrainState]
    stations: Optional[List[Dict[str, Any]]] = None
    schedules: Optional[List[Dict[str, Any]]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]


class ModelInfoResponse(BaseModel):
    models: Dict[str, Any]
