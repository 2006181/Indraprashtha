import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

import pandas as pd
import openpyxl

from ml.config import DATASET_DIR

logger = logging.getLogger(__name__)


class RailwayDataLoader:
    """
    Reusable data loader for Railway Datasets.
    Supports CSV, JSON, Excel (.xlsx), and Parquet files using pathlib.
    """

    def __init__(self, dataset_dir: Optional[Union[str, Path]] = None):
        self.dataset_dir = Path(dataset_dir) if dataset_dir else DATASET_DIR

    def _resolve_path(self, filename: str) -> Path:
        path = self.dataset_dir / filename
        if not path.exists():
            # Check nested train_dataset folder if present
            nested_path = self.dataset_dir / "train_dataset" / filename
            if nested_path.exists():
                return nested_path
            raise FileNotFoundError(f"Dataset file not found: {filename} in {self.dataset_dir}")
        return path

    def load_csv(self, filename: str) -> pd.DataFrame:
        path = self._resolve_path(filename)
        logger.info(f"Loading CSV: {path.name}")
        return pd.read_csv(path)

    def load_json(self, filename: str) -> List[Dict[str, Any]]:
        path = self._resolve_path(filename)
        logger.info(f"Loading JSON: {path.name}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_parquet(self, filename: str) -> pd.DataFrame:
        path = self._resolve_path(filename)
        logger.info(f"Loading Parquet: {path.name}")
        return pd.read_parquet(path)

    def load_excel(self, filename: str, sheet_name: Optional[str] = None) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        path = self._resolve_path(filename)
        logger.info(f"Loading Excel: {path.name}")
        if sheet_name:
            return pd.read_excel(path, sheet_name=sheet_name)
        return pd.read_excel(path, sheet_name=None)

    def load_all_datasets(self) -> Dict[str, Any]:
        """
        Loads all datasets from the dataset directory into a single dictionary.
        """
        datasets = {}
        
        # Load CSVs
        datasets["etrain_delays"] = self.load_csv("etrain_delays.csv")
        datasets["train_delay_prediction"] = self.load_csv("Train_delay_Prediction.csv")
        
        # Load Parquet / CSV stations
        try:
            datasets["india_railway_stations"] = self.load_parquet("india_railway_stations.parquet")
        except Exception:
            datasets["india_railway_stations"] = self.load_csv("india_railway_stations.csv")
            
        # Load JSON Train Schedules
        datasets["exp_trains"] = self.load_json("EXP-TRAINS.json")
        datasets["pass_trains"] = self.load_json("PASS-TRAINS.json")
        datasets["sf_trains"] = self.load_json("SF-TRAINS.json")

        # Load Excel Scheduling Data
        datasets["scheduling_excel"] = self.load_excel("Railway_Scheduling_Data.xlsx")

        logger.info("Successfully loaded all railway datasets.")
        return datasets
