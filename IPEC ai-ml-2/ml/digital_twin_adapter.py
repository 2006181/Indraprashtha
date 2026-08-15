import logging
from typing import Dict, Any, List, Optional

from ml.prediction_service import PredictionService
from ml.schemas import DigitalTwinState

logger = logging.getLogger(__name__)


class DigitalTwinAdapter:
    """
    Adapter interfacing Digital Twin simulated states with the AI/ML Prediction Engine.
    Produces machine-readable outputs for OR-Tools Optimization Engine consumption.
    """

    def __init__(self, service: Optional[PredictionService] = None):
        self.service = service or PredictionService()

    def predict_from_digital_twin_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses raw Digital Twin state dict, runs ETA, Delay, and Conflict predictions,
        and returns structured results for downstream OR-Tools optimizer.
        """
        timestamp = state.get("timestamp", "2026-08-16T00:00:00Z")
        trains = state.get("trains", [])
        
        train_predictions = []
        optimizer_records = []
        conflict_matrix = []

        # Predict for each train in current state
        for train in trains:
            train_id = str(train.get("train_id", train.get("train_number", "UNKNOWN")))
            train_type = train.get("train_type", "Express")
            station_code = train.get("station_code", train.get("station", "NDLS"))
            delay_mins = float(train.get("delay_minutes", 0.0))
            sched_time = float(train.get("scheduled_travel_time_mins", 180.0))
            dist_kms = float(train.get("distance_kms", 150.0))
            dep_hour = train.get("scheduled_departure_hour", 12)

            res = self.service.predict_all(
                train_id=train_id,
                train_type=train_type,
                station_code=station_code,
                scheduled_travel_time_mins=sched_time,
                distance_kms=dist_kms,
                historical_avg_delay=delay_mins,
                scheduled_departure_hour=dep_hour,
                prev_stop_delay=delay_mins
            )
            train_predictions.append(res)
            optimizer_records.append(res["optimizer_payload"])

        # Pairwise conflict detection across trains at shared stations
        for i in range(len(trains)):
            for j in range(i + 1, len(trains)):
                t1, t2 = trains[i], trains[j]
                s1 = t1.get("station_code", t1.get("station"))
                s2 = t2.get("station_code", t2.get("station"))

                if s1 == s2:
                    conf = self.service.predict_conflict(
                        train_id_a=str(t1.get("train_id")),
                        train_id_b=str(t2.get("train_id")),
                        station_code=s1,
                        scheduled_gap_mins=5.0,
                        time_difference_mins=5.0,
                        delay_a=float(t1.get("delay_minutes", 0.0)),
                        delay_b=float(t2.get("delay_minutes", 0.0)),
                        train_type_a=t1.get("train_type", "Express"),
                        train_type_b=t2.get("train_type", "Superfast")
                    )
                    conflict_matrix.append(conf)

        return {
            "timestamp": timestamp,
            "total_trains_processed": len(trains),
            "predictions": train_predictions,
            "conflicts": conflict_matrix,
            "optimizer_input": {
                "timestamp": timestamp,
                "train_status_list": optimizer_records,
                "potential_conflicts": conflict_matrix
            }
        }
