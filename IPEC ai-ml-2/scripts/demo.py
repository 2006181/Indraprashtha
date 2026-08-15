import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ml.data_loader import RailwayDataLoader
from ml.feature_engineering import extract_route_legs
from ml.prediction_service import PredictionService
from ml.model_registry import ModelRegistry


def main():
    registry = ModelRegistry()
    service = PredictionService(registry=registry)

    # Load a real sample from dataset
    loader = RailwayDataLoader()
    datasets = loader.load_all_datasets()
    df_legs = extract_route_legs(datasets)

    # Pick a real sample record
    sample = df_legs.dropna(subset=["dep_mins"]).iloc[15]
    real_train_id = str(sample["train_number"])
    real_train_type = str(sample["train_type"])
    real_station = str(sample["station_code"])
    real_station_name = str(sample["station_name"])
    real_dist = float(sample["distance_kms"])
    real_travel_time = float(sample["scheduled_travel_time_mins"]) if sample["scheduled_travel_time_mins"] > 0 else 120.0
    real_dep_hour = int(sample["dep_hour"]) if not sys.float_info.min > sample["dep_hour"] else 14

    # Run actual predictions through prediction service
    res = service.predict_all(
        train_id=real_train_id,
        train_type=real_train_type,
        station_code=real_station,
        scheduled_travel_time_mins=real_travel_time,
        distance_kms=real_dist,
        historical_avg_delay=20.0,
        scheduled_departure_hour=real_dep_hour,
        conflict_check_train_id="12674",
        conflict_scheduled_gap_mins=5.0
    )

    info = registry.get_info()
    eta_algo = info.get("metrics", {}).get("eta_model", {}).get("algorithm", "XGBoost / LightGBM")
    delay_algo = info.get("metrics", {}).get("delay_model", {}).get("algorithm", "XGBoost")
    conflict_method = res.get("conflict", {}).get("method", "ml").upper()

    print("============================================")
    print("SIH25022 AI RAILWAY PREDICTION ENGINE")
    print("============================================")
    print("")
    print("Dataset:")
    print("train_dataset.zip (Authoritative Ground Truth)")
    print("")
    print(f"Train:")
    print(f"{real_train_id} ({sample['train_name']})")
    print("")
    print(f"Train Type:")
    print(f"{real_train_type}")
    print("")
    print(f"Station:")
    print(f"{real_station} ({real_station_name})")
    print("")
    print("--------------------------------------------")
    print("ETA PREDICTION")
    print("--------------------------------------------")
    print("")
    print("Predicted ETA:")
    print(f"{res['eta']['predicted_eta_minutes']} minutes")
    print("")
    print("--------------------------------------------")
    print("DELAY PREDICTION")
    print("--------------------------------------------")
    print("")
    print("Predicted Delay:")
    print(f"{res['delay']['predicted_delay_minutes']} minutes")
    print("")
    print("--------------------------------------------")
    print("CONFLICT / TRAFFIC RISK")
    print("--------------------------------------------")
    print("")
    print("Risk:")
    print(f"{res['conflict']['risk_level']}")
    print("")
    print("Probability:")
    print(f"{res['conflict']['conflict_probability'] * 100:.1f}%")
    print("")
    print("--------------------------------------------")
    print("MODEL INFORMATION")
    print("--------------------------------------------")
    print("")
    print(f"ETA Model:")
    print(f"{eta_algo}")
    print("")
    print(f"Delay Model:")
    print(f"{delay_algo}")
    print("")
    print(f"Conflict:")
    print(f"{conflict_method}")
    print("")
    print("============================================")


if __name__ == "__main__":
    main()
