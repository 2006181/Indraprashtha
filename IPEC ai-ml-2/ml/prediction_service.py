import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from ml.model_registry import ModelRegistry
from ml.conflict_model import ConflictPredictionModel

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Unified Prediction Service serving ETA, Delay, Traffic Conflict, and Combined predictions.
    """

    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry or ModelRegistry()
        self.status = self.registry.load_all_models()

    def predict_eta(
        self,
        train_id: str,
        train_type: str,
        station_code: str,
        scheduled_travel_time_mins: Optional[float] = None,
        distance_kms: Optional[float] = None,
        historical_avg_delay: Optional[float] = None,
        scheduled_departure_hour: Optional[int] = None,
        day_of_week: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Predicts Train ETA / remaining journey duration in minutes.
        """
        input_data = pd.DataFrame([{
            "train_type": train_type,
            "station_code": station_code,
            "scheduled_travel_time_mins": scheduled_travel_time_mins if scheduled_travel_time_mins is not None else 180.0,
            "distance_kms": distance_kms if distance_kms is not None else 150.0,
            "remaining_distance": distance_kms if distance_kms is not None else 150.0,
            "historical_avg_delay": historical_avg_delay if historical_avg_delay is not None else 20.0,
            "station_delay_rate": historical_avg_delay if historical_avg_delay is not None else 20.0,
            "train_type_delay_rate": 25.0,
            "dwell_time_mins": 2.0,
            "is_junction": 1,
            "route_count": 5,
            "dep_hour": scheduled_departure_hour if scheduled_departure_hour is not None else 12,
            "day_of_week": day_of_week if day_of_week is not None else 1
        }])

        if self.registry.is_model_available("eta_model"):
            eta_model = self.registry.get_model("eta_model")
            predicted_val = float(eta_model.predict(input_data)[0])
        else:
            # Fallback calculation if model file not loaded
            base = scheduled_travel_time_mins if scheduled_travel_time_mins is not None else 180.0
            delay = historical_avg_delay if historical_avg_delay is not None else 20.0
            predicted_val = base + delay * 0.5

        predicted_val = max(1.0, round(predicted_val, 1))

        return {
            "train_id": train_id,
            "predicted_eta_minutes": predicted_val,
            "unit": "minutes",
            "model_version": "1.0.0"
        }

    def predict_delay(
        self,
        train_id: str,
        train_type: str,
        station_code: str,
        scheduled_departure_hour: Optional[int] = None,
        historical_avg_delay: Optional[float] = None,
        prev_stop_delay: Optional[float] = 0.0,
        day_of_week: Optional[int] = None,
        next_stops: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Predicts Train Delay in minutes and estimates downstream propagation.
        """
        input_data = pd.DataFrame([{
            "train_type": train_type,
            "station_code": station_code,
            "historical_avg_delay": historical_avg_delay if historical_avg_delay is not None else 25.0,
            "station_delay_rate": historical_avg_delay if historical_avg_delay is not None else 25.0,
            "train_type_delay_rate": 25.0,
            "dwell_time_mins": 2.0,
            "distance_kms": 100.0,
            "is_junction": 1,
            "route_count": 5,
            "dep_hour": scheduled_departure_hour if scheduled_departure_hour is not None else 12,
            "day_of_week": day_of_week if day_of_week is not None else 1
        }])

        if self.registry.is_model_available("delay_model"):
            delay_model = self.registry.get_model("delay_model")
            predicted_val = float(delay_model.predict(input_data)[0])
        else:
            predicted_val = historical_avg_delay if historical_avg_delay is not None else 15.0

        if prev_stop_delay and prev_stop_delay > 0:
            predicted_val = predicted_val * 0.4 + prev_stop_delay * 0.6

        predicted_val = max(0.0, round(predicted_val, 1))

        # Downstream propagation estimator
        downstream = []
        if next_stops:
            if self.registry.is_model_available("delay_model"):
                delay_model = self.registry.get_model("delay_model")
                downstream = delay_model.estimate_downstream_propagation(predicted_val, next_stops)

        return {
            "train_id": train_id,
            "predicted_delay_minutes": predicted_val,
            "downstream_propagation": downstream,
            "model_version": "1.0.0"
        }

    def predict_conflict(
        self,
        train_id_a: str,
        train_id_b: str,
        station_code: str,
        scheduled_gap_mins: float,
        time_difference_mins: float,
        delay_a: float = 0.0,
        delay_b: float = 0.0,
        train_type_a: str = "Express",
        train_type_b: str = "Superfast"
    ) -> Dict[str, Any]:
        """
        Predicts Traffic Conflict / Bottleneck Risk between train pairs.
        """
        input_data = pd.DataFrame([{
            "train_id_a": train_id_a,
            "train_id_b": train_id_b,
            "station_code": station_code,
            "scheduled_gap_mins": scheduled_gap_mins,
            "time_difference_mins": time_difference_mins,
            "delay_a": delay_a,
            "delay_b": delay_b,
            "train_type_a": train_type_a,
            "train_type_b": train_type_b,
            "station_route_count": 5,
            "is_junction": 1
        }])

        if self.registry.is_model_available("conflict_model"):
            conflict_model = self.registry.get_model("conflict_model")
            prob = float(conflict_model.predict_probability(input_data)[0])
            risk_level = ConflictPredictionModel.map_risk_level(prob)
            method = "ml"
        else:
            prob, risk_level = ConflictPredictionModel.schedule_based_conflict_risk(
                scheduled_gap_mins, time_difference_mins, delay_a, delay_b
            )
            method = "schedule_based"

        return {
            "train_id_a": train_id_a,
            "train_id_b": train_id_b,
            "station_code": station_code,
            "conflict_probability": round(prob, 4),
            "risk_level": risk_level,
            "method": method
        }

    def predict_all(
        self,
        train_id: str,
        train_type: str,
        station_code: str,
        scheduled_travel_time_mins: Optional[float] = None,
        distance_kms: Optional[float] = None,
        historical_avg_delay: Optional[float] = None,
        scheduled_departure_hour: Optional[int] = None,
        day_of_week: Optional[int] = None,
        prev_stop_delay: Optional[float] = 0.0,
        conflict_check_train_id: Optional[str] = None,
        conflict_scheduled_gap_mins: Optional[float] = 10.0
    ) -> Dict[str, Any]:
        """
        Executes ETA, Delay, and Conflict predictions in a single call.
        Returns a combined schema formatted for OR-Tools optimization.
        """
        eta_res = self.predict_eta(
            train_id=train_id,
            train_type=train_type,
            station_code=station_code,
            scheduled_travel_time_mins=scheduled_travel_time_mins,
            distance_kms=distance_kms,
            historical_avg_delay=historical_avg_delay,
            scheduled_departure_hour=scheduled_departure_hour,
            day_of_week=day_of_week
        )

        delay_res = self.predict_delay(
            train_id=train_id,
            train_type=train_type,
            station_code=station_code,
            scheduled_departure_hour=scheduled_departure_hour,
            historical_avg_delay=historical_avg_delay,
            prev_stop_delay=prev_stop_delay,
            day_of_week=day_of_week
        )

        conflict_res = None
        if conflict_check_train_id:
            conflict_res = self.predict_conflict(
                train_id_a=train_id,
                train_id_b=conflict_check_train_id,
                station_code=station_code,
                scheduled_gap_mins=conflict_scheduled_gap_mins or 10.0,
                time_difference_mins=conflict_scheduled_gap_mins or 10.0,
                delay_a=delay_res["predicted_delay_minutes"],
                delay_b=0.0,
                train_type_a=train_type
            )

        # Machine-readable payload for OR-Tools optimizer consumption
        optimizer_payload = {
            "train_id": train_id,
            "station_code": station_code,
            "predicted_eta_minutes": eta_res["predicted_eta_minutes"],
            "predicted_delay_minutes": delay_res["predicted_delay_minutes"],
            "conflict_probability": conflict_res["conflict_probability"] if conflict_res else 0.0,
            "risk_level": conflict_res["risk_level"] if conflict_res else "LOW",
            "priority_weight": 1.5 if train_type in ["Superfast", "Express"] else 1.0
        }

        return {
            "train_id": train_id,
            "station_code": station_code,
            "eta": eta_res,
            "delay": delay_res,
            "conflict": conflict_res,
            "optimizer_payload": optimizer_payload
        }
