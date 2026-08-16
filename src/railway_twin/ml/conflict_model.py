import math
from typing import List, Tuple, Dict, Any

class ConflictPredictionModel:
    def predict_conflict_probability(
        self,
        train_a_block: str,
        train_b_block: str,
        train_a_eta_sec: float,
        train_b_eta_sec: float,
        min_headway_sec: float = 180.0
    ) -> float:
        # Same block conflict
        if train_a_block == train_b_block:
            time_diff = abs(train_a_eta_sec - train_b_eta_sec)
            if time_diff < min_headway_sec:
                return 0.98  # Very high probability of conflict
            else:
                return 0.40
        return 0.02

    def is_conflict_predicted(self, prob: float, threshold: float = 0.5) -> bool:
        return prob >= threshold

    def evaluate_metrics(
        self,
        y_true: List[int],
        y_pred: List[int]
    ) -> Dict[str, float]:
        if len(y_true) != len(y_pred) or not y_true:
            raise ValueError("Invalid evaluation inputs")

        tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
        tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        return {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "fpr": round(fpr, 4),
            "fnr": round(fnr, 4)
        }
