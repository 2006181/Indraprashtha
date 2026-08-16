from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from .config import MODEL_PATH, FEATURES_PATH, DATA_DIR, RANDOM_SEED

FEATURES = [
    "priority",
    "current_delay_min",
    "speed_kmph",
    "max_speed_kmph",
    "distance_to_station_km",
    "traffic_density",
    "occupied_blocks",
    "trains_ahead",
    "hour",
    "is_freight",
    "is_express",
    "platform_pressure",
]


def build_synthetic_dataset(n=20000, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)

    priority = rng.integers(1, 6, n)
    current_delay = np.clip(rng.gamma(1.7, 3.0, n), 0, 35)
    speed = rng.uniform(25, 120, n)
    max_speed = np.maximum(speed, rng.uniform(70, 130, n))
    distance = rng.uniform(0.5, 15, n)
    traffic = rng.integers(0, 10, n)
    occupied = rng.integers(0, 15, n)
    trains_ahead = rng.integers(0, 8, n)
    hour = rng.integers(0, 24, n)
    is_freight = rng.binomial(1, 0.25, n)
    is_express = rng.binomial(1, 0.30, n)
    platform_pressure = rng.uniform(0, 1, n)

    # Synthetic target: future delay after ~15 minutes.
    # It is a simulation/training target, not real railway data.
    target = (
        current_delay * 0.72
        + traffic * 0.65
        + occupied * 0.38
        + trains_ahead * 0.95
        + is_freight * 2.2
        + platform_pressure * 3.5
        + np.maximum(0, 70 - speed) * 0.025
        - priority * 0.55
        + rng.normal(0, 1.5, n)
    )
    target = np.clip(target, 0, None)

    df = pd.DataFrame({
        "priority": priority,
        "current_delay_min": current_delay,
        "speed_kmph": speed,
        "max_speed_kmph": max_speed,
        "distance_to_station_km": distance,
        "traffic_density": traffic,
        "occupied_blocks": occupied,
        "trains_ahead": trains_ahead,
        "hour": hour,
        "is_freight": is_freight,
        "is_express": is_express,
        "platform_pressure": platform_pressure,
        "target_delay_after_15min": target,
    })
    return df


def train_model(n=20000):
    df = build_synthetic_dataset(n)
    dataset_path = DATA_DIR / "synthetic_delay_training.csv"
    df.to_csv(dataset_path, index=False)

    X = df[FEATURES]
    y = df["target_delay_after_15min"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    model = HistGradientBoostingRegressor(
        max_iter=250,
        learning_rate=0.06,
        max_leaf_nodes=31,
        l2_regularization=0.2,
        random_state=RANDOM_SEED,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    metrics = {
        "mae_minutes": round(float(mean_absolute_error(y_test, pred)), 3),
        "r2": round(float(r2_score(y_test, pred)), 3),
        "samples": int(len(df)),
        "target": "synthetic delay after 15 minutes",
    }

    joblib.dump(model, MODEL_PATH)
    FEATURES_PATH.write_text(json.dumps(FEATURES, indent=2))
    return metrics


def ensure_model():
    if not MODEL_PATH.exists():
        return train_model()
    return {"status": "already_trained", "model_path": str(MODEL_PATH)}


def load_model():
    ensure_model()
    return joblib.load(MODEL_PATH)


def _features_for_train(train, twin):
    active = [t for t in twin.trains.values() if t.status != "ARRIVED"]
    traffic_density = len(active)
    occupied_blocks = sum(
        1 for b in twin.network.blocks.values() if b.occupied_by
    )

    ordered = list(twin.network.blocks.keys())
    try:
        current_index = ordered.index(train.current_block)
    except ValueError:
        current_index = 0

    trains_ahead = sum(
        1 for t in active
        if t.train_id != train.train_id
        and ordered.index(t.current_block) > current_index
        if t.current_block in ordered
    )

    platform_pressure = min(
        1.0,
        sum(1 for t in active if t.status == "WAITING") / 5.0
    )

    hour = (twin.clock_minute // 60) % 24

    return {
        "priority": train.priority,
        "current_delay_min": train.current_delay_min,
        "speed_kmph": train.speed_kmph,
        "max_speed_kmph": train.max_speed_kmph,
        "distance_to_station_km": train.distance_to_station_km,
        "traffic_density": traffic_density,
        "occupied_blocks": occupied_blocks,
        "trains_ahead": trains_ahead,
        "hour": hour,
        "is_freight": int(train.train_type == "FREIGHT"),
        "is_express": int(train.train_type == "EXPRESS"),
        "platform_pressure": platform_pressure,
    }


def predict_for_train(train, twin):
    model = load_model()
    row = pd.DataFrame([_features_for_train(train, twin)])[FEATURES]
    prediction = float(model.predict(row)[0])
    return {
        "train_id": train.train_id,
        "predicted_delay_after_15min": round(max(0, prediction), 2),
        "features": row.iloc[0].to_dict(),
    }