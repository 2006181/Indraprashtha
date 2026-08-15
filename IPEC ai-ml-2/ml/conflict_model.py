import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier

from ml.config import RANDOM_SEED, TEST_SIZE, XGB_N_ESTIMATORS, XGB_MAX_DEPTH, XGB_LEARNING_RATE
from ml.preprocessing import build_preprocessor, get_feature_names

logger = logging.getLogger(__name__)


class ConflictPredictionModel:
    """
    Model 3: Train Conflict / Traffic Risk Prediction Model
    Predicts conflict probability between train pairs at shared station/track bottlenecks.
    """

    NUM_COLS = [
        "scheduled_gap_mins", "time_difference_mins", "delay_a", "delay_b",
        "station_route_count", "is_junction"
    ]
    CAT_COLS = ["train_type_a", "train_type_b", "station_code"]

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
        y = df["is_conflict"]
        return X, y

    def train(self, df_conflict: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Training Conflict / Traffic Risk Prediction Model (Model 3)...")
        X, y = self.prepare_features(df_conflict)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y if y.nunique() > 1 else None
        )

        self.preprocessor = build_preprocessor(self.NUM_COLS, self.CAT_COLS)
        X_train_trans = self.preprocessor.fit_transform(X_train)
        X_test_trans = self.preprocessor.transform(X_test)

        self.feature_names = get_feature_names(self.preprocessor, self.NUM_COLS, self.CAT_COLS)

        self.model = XGBClassifier(
            n_estimators=XGB_N_ESTIMATORS,
            max_depth=XGB_MAX_DEPTH,
            learning_rate=XGB_LEARNING_RATE,
            random_state=RANDOM_SEED,
            eval_metric="logloss"
        )
        self.model.fit(X_train_trans, y_train)

        preds = self.model.predict(X_test_trans)
        probs = self.model.predict_proba(X_test_trans)[:, 1] if hasattr(self.model, "predict_proba") else preds

        precision = float(precision_score(y_test, preds, zero_division=0))
        recall = float(recall_score(y_test, preds, zero_division=0))
        f1 = float(f1_score(y_test, preds, zero_division=0))
        try:
            roc_auc = float(roc_auc_score(y_test, probs))
        except Exception:
            roc_auc = 0.5

        cm = confusion_matrix(y_test, preds).tolist()

        # Feature Importance
        importances = self.model.feature_importances_
        fi_pairs = sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
        top_fi = {k: float(v) for k, v in fi_pairs}

        metrics = {
            "model_name": "Traffic Conflict Model",
            "algorithm": "XGBoostClassifier",
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "roc_auc": roc_auc,
            "confusion_matrix": cm,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "top_features": top_fi
        }

        logger.info(f"Conflict Model Trained. Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}, ROC-AUC: {roc_auc:.4f}")
        return metrics

    def predict_probability(self, input_df: pd.DataFrame) -> np.ndarray:
        for col in self.NUM_COLS:
            if col not in input_df.columns:
                input_df[col] = 0.0
        for col in self.CAT_COLS:
            if col not in input_df.columns:
                input_df[col] = "Unknown"

        X = input_df[self.NUM_COLS + self.CAT_COLS]
        X_trans = self.preprocessor.transform(X)
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X_trans)[:, 1]
        return self.model.predict(X_trans).astype(float)

    @staticmethod
    def map_risk_level(prob: float) -> str:
        if prob < 0.30:
            return "LOW"
        elif prob < 0.60:
            return "MEDIUM"
        elif prob < 0.80:
            return "HIGH"
        else:
            return "CRITICAL"

    @classmethod
    def schedule_based_conflict_risk(
        cls,
        scheduled_gap_mins: float,
        time_difference_mins: float,
        delay_a: float = 0.0,
        delay_b: float = 0.0
    ) -> Tuple[float, str]:
        """
        Rule-based timetable conflict risk calculation when ML input is unavailable.
        """
        effective_gap = abs((time_difference_mins + delay_a) - delay_b)
        if effective_gap <= 3.0:
            prob = 0.95
        elif effective_gap <= 7.0:
            prob = 0.75
        elif effective_gap <= 15.0:
            prob = 0.45
        else:
            prob = 0.10

        return float(prob), cls.map_risk_level(prob)
