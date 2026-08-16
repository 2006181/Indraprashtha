import math
from typing import List, Tuple

class DelayPredictionModel:
    def predict_downstream_delay(
        self,
        current_delay: float,
        traffic_density: float,  # 0.0 to 1.0
        train_priority: int,
        is_section_blocked: bool = False
    ) -> float:
        if current_delay < 0:
            raise ValueError("Current delay cannot be negative")
        
        if is_section_blocked:
            predicted = current_delay + 20.0 + (10 - train_priority) * 2.0
        else:
            multipler = 1.0 + (traffic_density * 0.5)
            priority_discount = max(0.0, (train_priority - 1) * 0.03)
            predicted = current_delay * (multipler - priority_discount)

        if math.isnan(predicted) or math.isinf(predicted) or predicted < 0:
            raise ValueError("Invalid delay prediction output")

        return round(predicted, 2)

    def evaluate_metrics(self, y_true: List[float], y_pred: List[float]) -> Tuple[float, float, float]:
        if len(y_true) != len(y_pred) or not y_true:
            raise ValueError("Invalid dataset length for evaluation")
        
        n = len(y_true)
        mae = sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n
        rmse = math.sqrt(sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n)
        
        mean_true = sum(y_true) / n
        ss_tot = sum((t - mean_true) ** 2 for t in y_true)
        ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
        
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
        return round(mae, 4), round(rmse, 4), round(r2, 4)
