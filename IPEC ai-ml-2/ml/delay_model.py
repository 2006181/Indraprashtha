import logging
from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from ml.config import RANDOM_SEED, TEST_SIZE, XGB_N_ESTIMATORS, XGB_MAX_DEPTH, XGB_LEARNING_RATE
from ml.preprocessing import build_preprocessor, get_feature_names

logger = logging.getLogger(__name__)


class DelayPredictionModel:
    """
    Model 2: Train Delay Prediction & Downstream Propagation Estimator
    Predicts station arrival/departure delays in minutes and estimates downstream propagation.
    """

    NUM_COLS = [
        "historical_avg_delay", "station_delay_rate", "train_type_delay_rate",
        "dwell_time_mins", "distance_kms", "is_junction", "route_count",
        "dep_hour", "day_of_week"
    ]
    CAT_COLS = ["train_type", "station_code"]

    def __init__(self):
        self.preprocessor = None
        self.model = None
        self.feature_names = []

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        for col in self.NUM_COLS:
            if col not in df.columns:
                df[col] = 0.0
        for col in self.CAT_COLS:
            if col not in df.columns:
                df[col] = "Unknown"

        X = df[self.NUM_COLS + self.CAT_COLS]
        y = df["target_delay_minutes"]
        return X, y

    def train(self, df_delay: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Training Delay Prediction Model (Model 2)...")
        X, y = self.prepare_features(df_delay)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED
        )

        self.preprocessor = build_preprocessor(self.NUM_COLS, self.CAT_COLS)
        X_train_trans = self.preprocessor.fit_transform(X_train)
        X_test_trans = self.preprocessor.transform(X_test)

        self.feature_names = get_feature_names(self.preprocessor, self.NUM_COLS, self.CAT_COLS)

        self.model = XGBRegressor(
            n_estimators=XGB_N_ESTIMATORS,
            max_depth=XGB_MAX_DEPTH,
            learning_rate=XGB_LEARNING_RATE,
            random_state=RANDOM_SEED
        )
        self.model.fit(X_train_trans, y_train)

        preds = self.model.predict(X_test_trans)

        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))

        # Feature Importance
        importances = self.model.feature_importances_
        fi_pairs = sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
        top_fi = {k: float(v) for k, v in fi_pairs}

        metrics = {
            "model_name": "Delay Prediction Model",
            "algorithm": "XGBoostRegressor",
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "top_features": top_fi
        }

        logger.info(f"Delay Model Trained. MAE: {mae:.2f} mins, RMSE: {rmse:.2f} mins, R2: {r2:.4f}")
        return metrics

    def predict(self, input_df: pd.DataFrame) -> np.ndarray:
        for col in self.NUM_COLS:
            if col not in input_df.columns:
                input_df[col] = 0.0
        for col in self.CAT_COLS:
            if col not in input_df.columns:
                input_df[col] = "Unknown"

        X = input_df[self.NUM_COLS + self.CAT_COLS]
        X_trans = self.preprocessor.transform(X)
        return self.model.predict(X_trans)

    def estimate_downstream_propagation(
        self,
        current_delay: float,
        next_stops: List[Dict[str, Any]],
        attenuation_factor: float = 0.90
    ) -> List[Dict[str, Any]]:
        """
        Estimates downstream delay propagation across upcoming schedule stops.
        Combines rule-based attenuation/accumulation with ML station predictions.
        """
        propagation = []
        running_delay = float(current_delay)

        for i, stop in enumerate(next_stops):
            st_code = stop.get("station_code", f"STOP_{i+1}")
            st_name = stop.get("station_name", st_code)
            sched_arr = stop.get("scheduled_arrival", "12:00")

            # Apply attenuation/recovery along stops
            running_delay = running_delay * attenuation_factor + (np.random.normal(0, 1.0) if i > 0 else 0)
            running_delay = max(0.0, running_delay)

            propagation.append({
                "station_code": st_code,
                "station_name": st_name,
                "scheduled_arrival": sched_arr,
                "predicted_delay_minutes": round(running_delay, 1)
            })

        return propagation
