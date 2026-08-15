import json
import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ml.config import PLOT_DIR, REPORT_DIR, RANDOM_SEED, TEST_SIZE
from ml.data_loader import RailwayDataLoader
from ml.feature_engineering import build_unified_ml_features
from ml.model_registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_plots():
    logger.info("==================================================")
    logger.info("STARTING MODEL EVALUATION & PLOT GENERATION")
    logger.info("==================================================")

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    registry = ModelRegistry()

    if not registry.is_model_available("eta_model"):
        logger.error("Trained models not found. Run scripts/train_all.py first!")
        return

    loader = RailwayDataLoader()
    datasets = loader.load_all_datasets()
    df_eta, df_delay, df_conflict = build_unified_ml_features(datasets)

    eta_model = registry.get_model("eta_model")
    delay_model = registry.get_model("delay_model")
    conflict_model = registry.get_model("conflict_model")

    # 1. ETA Plots
    X_eta, y_eta = eta_model.prepare_features(df_eta)
    _, X_test_eta, _, y_test_eta = train_test_split(X_eta, y_eta, test_size=TEST_SIZE, random_state=RANDOM_SEED)
    eta_preds = eta_model.predict(X_test_eta)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test_eta, eta_preds, alpha=0.5, color="blue", edgecolors="k", s=20)
    plt.plot([y_test_eta.min(), y_test_eta.max()], [y_test_eta.min(), y_test_eta.max()], "r--", lw=2)
    plt.xlabel("Actual Scheduled Travel Time + Delay (mins)")
    plt.ylabel("Predicted ETA (mins)")
    plt.title("Model 1: ETA Prediction — Actual vs Predicted")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "eta_actual_vs_predicted.png", dpi=300)
    plt.close()

    # ETA Residual Distribution
    residuals_eta = y_test_eta - eta_preds
    plt.figure(figsize=(8, 6))
    plt.hist(residuals_eta, bins=30, color="teal", edgecolor="black", alpha=0.7)
    plt.axvline(0, color="red", linestyle="--", lw=2)
    plt.xlabel("Residual (Actual - Predicted mins)")
    plt.ylabel("Frequency")
    plt.title("Model 1: ETA Residual Error Distribution")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "eta_residuals.png", dpi=300)
    plt.close()

    # 2. Delay Plots
    X_del, y_del = delay_model.prepare_features(df_delay)
    _, X_test_del, _, y_test_del = train_test_split(X_del, y_del, test_size=TEST_SIZE, random_state=RANDOM_SEED)
    del_preds = delay_model.predict(X_test_del)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test_del, del_preds, alpha=0.5, color="purple", edgecolors="k", s=20)
    plt.plot([y_test_del.min(), y_test_del.max()], [y_test_del.min(), y_test_del.max()], "r--", lw=2)
    plt.xlabel("Actual Station Delay (mins)")
    plt.ylabel("Predicted Station Delay (mins)")
    plt.title("Model 2: Delay Prediction — Actual vs Predicted")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "delay_actual_vs_predicted.png", dpi=300)
    plt.close()

    # Delay Feature Importance
    top_fi_del = registry.load_metadata().get("metrics", {}).get("delay_model", {}).get("top_features", {})
    if top_fi_del:
        plt.figure(figsize=(10, 6))
        features = list(top_fi_del.keys())[::-1]
        scores = list(top_fi_del.values())[::-1]
        plt.barh(features, scores, color="mediumseagreen", edgecolor="black")
        plt.xlabel("Feature Importance Score")
        plt.title("Model 2: Delay Model Top Important Features")
        plt.tight_layout()
        plt.savefig(PLOT_DIR / "delay_feature_importance.png", dpi=300)
        plt.close()

    # 3. Conflict Plots
    X_conf, y_conf = conflict_model.prepare_features(df_conflict)
    _, X_test_conf, _, y_test_conf = train_test_split(
        X_conf, y_conf, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y_conf if y_conf.nunique() > 1 else None
    )
    conf_probs = conflict_model.predict_probability(X_test_conf)

    # Risk Distribution Bar Chart
    risk_levels = [conflict_model.map_risk_level(p) for p in conf_probs]
    counts = pd.Series(risk_levels).value_counts()
    
    plt.figure(figsize=(8, 6))
    colors = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red", "CRITICAL": "darkred"}
    bar_colors = [colors.get(k, "blue") for k in counts.index]
    plt.bar(counts.index, counts.values, color=bar_colors, edgecolor="black")
    plt.xlabel("Traffic Risk Level")
    plt.ylabel("Number of Pairs")
    plt.title("Model 3: Conflict / Traffic Risk Category Distribution")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "conflict_risk_distribution.png", dpi=300)
    plt.close()

    logger.info(f"Successfully generated all plots in: {PLOT_DIR}")


if __name__ == "__main__":
    generate_plots()
