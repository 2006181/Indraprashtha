import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data" / "railway"))
DATASET_DIR = DATA_DIR / "train_dataset"
MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "ml" / "models"))
REPORT_DIR = Path(os.getenv("REPORT_DIR", BASE_DIR / "reports"))
PLOT_DIR = REPORT_DIR / "plots"

# Ensure directories exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Training Hyperparameters
RANDOM_SEED = 42
TEST_SIZE = 0.2
XGB_N_ESTIMATORS = 200
XGB_MAX_DEPTH = 6
XGB_LEARNING_RATE = 0.05

# FastAPI Settings
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
