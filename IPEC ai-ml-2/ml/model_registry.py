import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import joblib

from ml.config import MODEL_DIR

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Registry for loading, saving, and version management of trained ML models.
    """

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = Path(model_dir) if model_dir else MODEL_DIR
        self.metadata_path = self.model_dir / "metadata.json"
        self._models = {}
        self._metadata = {}

    def save_model(self, model_key: str, model_object: Any):
        self.model_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.model_dir / f"{model_key}.joblib"
        joblib.dump(model_object, file_path)
        logger.info(f"Saved model '{model_key}' to {file_path}")

    def save_metadata(self, metadata: Dict[str, Any]):
        self.model_dir.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        self._metadata = metadata
        logger.info(f"Saved model registry metadata to {self.metadata_path}")

    def load_model(self, model_key: str) -> Any:
        file_path = self.model_dir / f"{model_key}.joblib"
        if not file_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")
        model = joblib.load(file_path)
        self._models[model_key] = model
        logger.info(f"Loaded model '{model_key}' from {file_path}")
        return model

    def load_metadata(self) -> Dict[str, Any]:
        if not self.metadata_path.exists():
            return {}
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self._metadata = json.load(f)
        return self._metadata

    def is_model_available(self, model_key: str) -> bool:
        file_path = self.model_dir / f"{model_key}.joblib"
        return file_path.exists()

    def load_all_models(self) -> Dict[str, bool]:
        status = {}
        for key in ["eta_model", "delay_model", "conflict_model"]:
            if self.is_model_available(key):
                try:
                    self.load_model(key)
                    status[key] = True
                except Exception as e:
                    logger.error(f"Error loading {key}: {e}")
                    status[key] = False
            else:
                status[key] = False
        self.load_metadata()
        return status

    def get_model(self, model_key: str) -> Any:
        if model_key not in self._models:
            return self.load_model(model_key)
        return self._models[model_key]

    def get_info(self) -> Dict[str, Any]:
        meta = self.load_metadata()
        available = {key: self.is_model_available(key) for key in ["eta_model", "delay_model", "conflict_model"]}
        return {
            "version": meta.get("version", "1.0.0"),
            "training_date": meta.get("training_date", "Unknown"),
            "available_models": available,
            "metrics": meta.get("metrics", {})
        }
