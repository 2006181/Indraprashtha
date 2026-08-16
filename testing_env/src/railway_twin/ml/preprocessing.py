import math
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class RawFeatureInput:
    speed: float
    distance: float
    train_type: str
    current_delay: float
    block_id: str
    time_of_day_seconds: float

class FeaturePreprocessor:
    VALID_TRAIN_TYPES = {"EXPRESS", "PASSENGER", "FREIGHT"}

    def validate(self, input_data: RawFeatureInput) -> bool:
        if math.isnan(input_data.speed) or math.isinf(input_data.speed):
            return False
        if math.isnan(input_data.distance) or math.isinf(input_data.distance):
            return False
        if math.isnan(input_data.current_delay) or math.isinf(input_data.current_delay):
            return False
        if input_data.speed < 0 or input_data.distance < 0 or input_data.current_delay < 0:
            return False
        if input_data.train_type not in self.VALID_TRAIN_TYPES:
            return False
        return True

    def preprocess(self, input_data: RawFeatureInput) -> List[float]:
        if not self.validate(input_data):
            raise ValueError(f"Invalid feature input: {input_data}")
        
        # One-hot encode train_type
        type_vec = [
            1.0 if input_data.train_type == "EXPRESS" else 0.0,
            1.0 if input_data.train_type == "PASSENGER" else 0.0,
            1.0 if input_data.train_type == "FREIGHT" else 0.0
        ]
        
        # Scaled numeric features
        norm_speed = input_data.speed / 160.0
        norm_dist = input_data.distance / 100.0
        norm_delay = input_data.current_delay / 120.0
        norm_time = input_data.time_of_day_seconds / 86400.0

        return [norm_speed, norm_dist, norm_delay, norm_time] + type_vec
