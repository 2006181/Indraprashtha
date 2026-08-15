import datetime
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ml.config import MODEL_DIR, REPORT_DIR, RANDOM_SEED
from ml.data_loader import RailwayDataLoader
from ml.data_validator import DataValidator
from ml.feature_engineering import build_unified_ml_features
from ml.eta_model import ETAPredictionModel
from ml.delay_model import DelayPredictionModel
from ml.conflict_model import ConflictPredictionModel
from ml.model_registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("==================================================")
    logger.info("STARTING SIH25022 AI/ML MODEL TRAINING PIPELINE")
    logger.info("==================================================")

    # 1. Ingest Dataset
    loader = RailwayDataLoader()
    datasets = loader.load_all_datasets()

    # 2. Validate Data Quality
    logger.info("Running Data Quality Validation...")
    validator = DataValidator(loader)
    quality_report = validator.validate_all()
    logger.info(f"Data Quality Validation Complete. Total Issues Identified: {quality_report['summary']['total_issues_found']}")

    # 3. Feature Engineering & Dataset Fusion
    logger.info("Fusing Datasets and Engineering Features...")
    df_eta, df_delay, df_conflict = build_unified_ml_features(datasets)

    # 4. Train Model 1: ETA Model
    logger.info("--------------------------------------------------")
    eta_trainer = ETAPredictionModel()
    eta_metrics = eta_trainer.train(df_eta)

    # 5. Train Model 2: Delay Model
    logger.info("--------------------------------------------------")
    delay_trainer = DelayPredictionModel()
    delay_metrics = delay_trainer.train(df_delay)

    # 6. Train Model 3: Conflict Model
    logger.info("--------------------------------------------------")
    conflict_trainer = ConflictPredictionModel()
    conflict_metrics = conflict_trainer.train(df_conflict)

    # 7. Save Model Artifacts & Registry Metadata
    logger.info("--------------------------------------------------")
    registry = ModelRegistry(MODEL_DIR)
    registry.save_model("eta_model", eta_trainer)
    registry.save_model("delay_model", delay_trainer)
    registry.save_model("conflict_model", conflict_trainer)

    metadata = {
        "version": "1.0.0",
        "training_date": datetime.datetime.now().isoformat(),
        "random_seed": RANDOM_SEED,
        "dataset_name": "train_dataset.zip",
        "dataset_rows": {
            "eta_samples": len(df_eta),
            "delay_samples": len(df_delay),
            "conflict_samples": len(df_conflict)
        },
        "metrics": {
            "eta_model": eta_metrics,
            "delay_model": delay_metrics,
            "conflict_model": conflict_metrics
        }
    }
    registry.save_metadata(metadata)

    # Save metrics JSON files
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_DIR / "eta_metrics.json", "w", encoding="utf-8") as f:
        json.dump(eta_metrics, f, indent=2)

    with open(REPORT_DIR / "delay_metrics.json", "w", encoding="utf-8") as f:
        json.dump(delay_metrics, f, indent=2)

    with open(REPORT_DIR / "conflict_metrics.json", "w", encoding="utf-8") as f:
        json.dump(conflict_metrics, f, indent=2)

    feature_importance = {
        "eta_model": eta_metrics.get("top_features", {}),
        "delay_model": delay_metrics.get("top_features", {}),
        "conflict_model": conflict_metrics.get("top_features", {})
    }
    with open(REPORT_DIR / "feature_importance.json", "w", encoding="utf-8") as f:
        json.dump(feature_importance, f, indent=2)

    logger.info("==================================================")
    logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info(f"Models saved in: {MODEL_DIR}")
    logger.info(f"Reports saved in: {REPORT_DIR}")
    logger.info("==================================================")


if __name__ == "__main__":
    main()
