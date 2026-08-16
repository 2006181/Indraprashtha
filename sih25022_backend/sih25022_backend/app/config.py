from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

MODEL_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "delay_model.joblib"
FEATURES_PATH = MODEL_DIR / "features.json"

RANDOM_SEED = 42
SIM_STEP_MINUTES = 1
DEFAULT_HORIZON_MINUTES = 30