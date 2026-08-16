from typing import Literal, Optional
from pydantic import BaseModel, Field


class Train(BaseModel):
    train_id: str
    train_type: Literal["EXPRESS", "PASSENGER", "FREIGHT", "LOCAL"]
    priority: int = Field(ge=1, le=5)
    origin: str
    destination: str
    current_block: str
    next_block: Optional[str] = None
    speed_kmph: float = Field(ge=0)
    max_speed_kmph: float = Field(gt=0)
    scheduled_arrival_min: int
    scheduled_departure_min: int
    current_delay_min: float = 0
    distance_to_station_km: float = Field(ge=0)
    status: Literal["RUNNING", "WAITING", "ARRIVED"] = "RUNNING"


class TrainCreate(BaseModel):
    train_id: str
    train_type: Literal["EXPRESS", "PASSENGER", "FREIGHT", "LOCAL"] = "PASSENGER"
    priority: int = Field(default=3, ge=1, le=5)
    origin: str
    destination: str
    start_block: str
    speed_kmph: float = Field(default=60, ge=0)
    max_speed_kmph: float = Field(default=100, gt=0)
    scheduled_arrival_min: int = 60
    scheduled_departure_min = 65


class DelayPredictionRequest(BaseModel):
    train_id: str


class ScenarioRequest(BaseModel):
    train_id: str
    delay_minutes: float = Field(gt=0, le=120)
    horizon_minutes: int = Field(default=30, ge=1, le=180)


class StepRequest(BaseModel):
    minutes: int = Field(default=1, ge=1, le=60)


class OptimizationRequest(BaseModel):
    block_id: Optional[str] = None
    horizon_minutes: int = Field(default=30, ge=5, le=180)


class SequenceResponse(BaseModel):
    block_id: str
    ordered_train_ids: list[str]
    objective_value: float
    explanation: str


class ScenarioResult(BaseModel):
    baseline: dict
    scenario: dict
    improvement: dict