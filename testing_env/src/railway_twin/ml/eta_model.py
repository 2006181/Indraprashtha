import math
from .preprocessing import RawFeatureInput, FeaturePreprocessor

class ETAPredictionModel:
    def __init__(self):
        self.preprocessor = FeaturePreprocessor()

    def predict_eta_minutes(self, raw_input: RawFeatureInput) -> float:
        if not self.preprocessor.validate(raw_input):
            raise ValueError("Invalid features passed to ETA model")
        
        speed = raw_input.speed
        dist = raw_input.distance
        delay = raw_input.current_delay

        # Handle zero or near-zero speed
        if speed <= 1e-3:
            effective_speed = 10.0  # Fallback minimum movement speed for ETA estimate
        else:
            effective_speed = speed

        # Base travel time in hours -> minutes
        base_eta = (dist / effective_speed) * 60.0
        
        # Add current delay and small buffer based on train type
        buffer_factor = 1.05 if raw_input.train_type == "FREIGHT" else 1.0
        predicted_eta = (base_eta + delay) * buffer_factor

        # Assert no negative travel time, NaN, or infinity
        if math.isnan(predicted_eta) or math.isinf(predicted_eta) or predicted_eta < 0:
            raise ValueError(f"ETA Prediction returned invalid value: {predicted_eta}")

        return round(predicted_eta, 2)
