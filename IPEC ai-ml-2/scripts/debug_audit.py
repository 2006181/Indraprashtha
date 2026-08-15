import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ml.data_loader import RailwayDataLoader
from ml.feature_engineering import parse_time_to_minutes, extract_route_legs, build_unified_ml_features
from ml.model_registry import ModelRegistry
from ml.prediction_service import PredictionService
from ml.digital_twin_adapter import DigitalTwinAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def audit_time_parser():
    logger.info("1. Auditing Time Parser Edge Cases...")
    assert np.isnan(parse_time_to_minutes("Source")), "Failed: Source time should return NaN"
    assert np.isnan(parse_time_to_minutes("Destination")), "Failed: Destination time should return NaN"
    assert np.isnan(parse_time_to_minutes("")), "Failed: Empty string should return NaN"
    assert np.isnan(parse_time_to_minutes(None)), "Failed: None should return NaN"
    assert parse_time_to_minutes("00:00", day=1) == 0.0, "Failed: 00:00 Day 1 should be 0.0"
    assert parse_time_to_minutes("23:59", day=1) == 1439.0, "Failed: 23:59 Day 1 should be 1439.0"
    assert parse_time_to_minutes("00:00", day=2) == 1440.0, "Failed: 00:00 Day 2 should be 1440.0"
    logger.info("✅ Time Parser Edge Cases Passed.")


def audit_prediction_service_edge_cases():
    logger.info("2. Auditing Prediction Service Edge Cases...")
    registry = ModelRegistry()
    service = PredictionService(registry=registry)

    # Edge Case 1: Unseen Train ID and Unseen Station Code
    res_unseen = service.predict_eta(
        train_id="UNKNOWN_99999",
        train_type="Superfast",
        station_code="UNSEEN_STATION",
        scheduled_travel_time_mins=0.0,
        distance_kms=0.0,
        historical_avg_delay=0.0
    )
    assert res_unseen["predicted_eta_minutes"] >= 1.0, f"Failed unseen station ETA: {res_unseen}"
    logger.info(f"✅ Unseen Station ETA Prediction: {res_unseen['predicted_eta_minutes']} mins")

    # Edge Case 2: Extreme High Delay (500 minutes)
    res_high_delay = service.predict_delay(
        train_id="12673",
        train_type="Express",
        station_code="MAS",
        historical_avg_delay=500.0,
        prev_stop_delay=300.0
    )
    assert res_high_delay["predicted_delay_minutes"] > 0.0, f"Failed high delay: {res_high_delay}"
    logger.info(f"✅ Extreme High Delay Prediction: {res_high_delay['predicted_delay_minutes']} mins")

    # Edge Case 3: Conflict with 0 gap
    res_conflict = service.predict_conflict(
        train_id_a="12673",
        train_id_b="12674",
        station_code="MAS",
        scheduled_gap_mins=0.0,
        time_difference_mins=0.0,
        delay_a=50.0,
        delay_b=50.0
    )
    assert res_conflict["risk_level"] in ["HIGH", "CRITICAL"], f"Failed 0 gap conflict risk: {res_conflict}"
    logger.info(f"✅ Zero Scheduled Gap Conflict Risk: {res_conflict['risk_level']} (Prob: {res_conflict['conflict_probability']})")

    # Edge Case 4: Combined Predict All with missing optional fields
    res_all = service.predict_all(
        train_id="99999",
        train_type="Passenger",
        station_code="XYZ"
    )
    assert "eta" in res_all and "delay" in res_all and "optimizer_payload" in res_all, "Failed predict_all edge case"
    logger.info("✅ Predict All Edge Cases Passed.")


def audit_digital_twin_adapter():
    logger.info("3. Auditing Digital Twin Adapter Edge Cases...")
    adapter = DigitalTwinAdapter()

    # Empty trains list
    empty_state = {"timestamp": "2026-08-16T00:00:00Z", "trains": []}
    res_empty = adapter.predict_from_digital_twin_state(empty_state)
    assert res_empty["total_trains_processed"] == 0, "Failed empty state processing"

    # Partial attributes
    partial_state = {
        "timestamp": "2026-08-16T00:00:00Z",
        "trains": [{"train_id": "T001", "station": "NDLS"}]
    }
    res_partial = adapter.predict_from_digital_twin_state(partial_state)
    assert res_partial["total_trains_processed"] == 1, "Failed partial state processing"
    logger.info("✅ Digital Twin Adapter Edge Cases Passed.")


def main():
    logger.info("==================================================")
    logger.info("STARTING DETAILED DEBUGGING & SYSTEM AUDIT")
    logger.info("==================================================")
    audit_time_parser()
    audit_prediction_service_edge_cases()
    audit_digital_twin_adapter()
    logger.info("==================================================")
    logger.info("ALL SYSTEM DEBUG AUDITS PASSED CLEANLY!")
    logger.info("==================================================")


if __name__ == "__main__":
    main()
