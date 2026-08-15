import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from ml.config import RANDOM_SEED, TEST_SIZE, XGB_N_ESTIMATORS, XGB_MAX_DEPTH, XGB_LEARNING_RATE
from ml.preprocessing import build_preprocessor, get_feature_names

logger = logging.getLogger(__name__)


class ETAPredictionModel:
    """
    Model 1: Train ETA Prediction Model
    Predicts remaining/total travel time in minutes.
    """

    NUM_COLS = [
        "scheduled_travel_time_mins", "distance_kms", "remaining_distance",
        "historical_avg_delay", "station_delay_rate", "train_type_delay_rate",
        "dwell_time_mins", "is_junction", "route_count", "dep_hour", "day_of_week"
    ]
    CAT_COLS = ["train_type", "station_code"]

    def __init__(self):
        self.preprocessor = None
        self.model = None
        self.feature_names = []

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        # Ensure all columns present
        for col in self.NUM_COLS:
            if col not in df.columns:
                df[col] = 0.0
        for col in self.CAT_COLS:
            if col not in df.columns:
                df[col] = "Unknown"

        X = df[self.NUM_COLS + self.CAT_COLS]
        y = df["target_eta_minutes"]
        return X, y

    def train(self, df_eta: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Training ETA Prediction Model (Model 1)...")
        X, y = self.prepare_features(df_eta)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED
        )

        self.preprocessor = build_preprocessor(self.NUM_COLS, self.CAT_COLS)
        X_train_trans = self.preprocessor.fit_transform(X_train)
        X_test_trans = self.preprocessor.transform(X_test)

        self.feature_names = get_feature_names(self.preprocessor, self.NUM_COLS, self.CAT_COLS)

        # Compare XGBoost vs LightGBM
        xgb_candidate = XGBRegressor(
            n_estimators=XGB_N_ESTIMATORS,
            max_depth=XGB_MAX_DEPTH,
            learning_rate=XGB_LEARNING_RATE,
            random_state=RANDOM_SEED
        )
        xgb_candidate.fit(X_train_trans, y_train)
        xgb_preds = xgb_candidate.predict(X_test_trans)
        xgb_mae = mean_absolute_error(y_test, xgb_preds)

        lgb_candidate = LGBMRegressor(
            n_estimators=XGB_N_ESTIMATORS,
            max_depth=XGB_MAX_DEPTH,
            learning_rate=XGB_LEARNING_RATE,
            random_state=RANDOM_SEED,
            verbose=-1
        )
        lgb_candidate.fit(X_train_trans, y_train)
        lgb_preds = lgb_candidate.predict(X_test_trans)
        lgb_mae = mean_absolute_error(y_test, lgb_preds)

        if lgb_mae < xgb_mae:
            logger.info(f"Selected LightGBM for ETA model (MAE: {lgb_mae:.4f} vs XGB MAE: {xgb_mae:.4f})")
            self.model = lgb_candidate
            preds = lgb_preds
            algo_name = "LightGBMRegressor"
        else:
            logger.info(f"Selected XGBoost for ETA model (MAE: {xgb_mae:.4f} vs LGB MAE: {lgb_mae:.4f})")
            self.model = xgb_candidate
            preds = xgb_preds
            algo_name = "XGBoostRegressor"

        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))
        mape = float(np.mean(np.abs((y_test - preds) / np.maximum(y_test, 1.0))) * 100)

        # Feature Importance
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            fi_pairs = sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
            top_fi = {k: float(v) for k, v in fi_pairs}
        else:
            top_fi = {}

        metrics = {
            "model_name": "ETA Prediction Model",
            "algorithm": algo_name,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "mape": mape,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "top_features": top_fi
        }

        logger.info(f"ETA Model Trained. MAE: {mae:.2f} mins, RMSE: {rmse:.2f} mins, R2: {r2:.4f}")
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
