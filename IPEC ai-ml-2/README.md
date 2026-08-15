# SIH25022 — AI/ML Prediction Engine
## Maximizing Section Throughput Using AI-Powered Precise Train Traffic Control

Welcome to the standalone AI/ML Prediction Engine for **SIH25022** (Smart India Hackathon 2025). This module serves as the predictive intelligence core for our Railway Digital Twin + Train Traffic Control & Optimization system.

---

## Architecture & Integration Flow

```
+---------------------+
| train_dataset.zip   |  <-- Authoritative Dataset (NO synthetic/fake data)
+---------------------+
           |
           v
+---------------------+
| Data Ingestion      |  <-- ml/data_loader.py (CSV, JSON, XLSX, Parquet)
+---------------------+
           |
           v
+---------------------+
| Data Quality Check  |  <-- ml/data_validator.py -> reports/data_quality_report.json
+---------------------+
           |
           v
+---------------------+
| Preprocessing &     |  <-- ml/preprocessing.py (scikit-learn ColumnTransformer)
| Feature Engineering |  <-- ml/feature_engineering.py (170k+ route leg stops fused)
+---------------------+
           |
      +----+----+----+
      |         |    |
      v         v    v
  +-------+ +-------+ +----------+
  |  ETA  | | Delay | | Conflict |  <-- Models 1, 2, 3 (XGBoost / LightGBM)
  +-------+ +-------+ +----------+
      |         |    |
      +----+----+----+
           |
           v
+---------------------+
| Model Registry &    |  <-- ml/model_registry.py
| Prediction Service  |  <-- ml/prediction_service.py
+---------------------+
           |
           v
+---------------------+
| FastAPI REST Engine |  <-- ml/prediction_api.py (GET /health, POST /predict/*)
+---------------------+
           |
      +----+----+
      |         |
      v         v
+--------------+ +----------------------+
| Digital Twin | | OR-Tools Optimizer   | <-- Machine-readable prediction payloads
+--------------+ +----------------------+
```

---

## 1. Dataset Description & Structure

The engine is built exclusively upon the authoritative `train_dataset.zip` dataset located in `data/railway/`:

- **`etrain_delays.csv`**: 1,900 historical delay records across 90 trains and 480 stations with delay distributions (`average_delay_minutes`, `pct_right_time`, `pct_slight_delay`, `pct_significant_delay`).
- **`EXP-TRAINS.json`** (2,533 trains), **`PASS-TRAINS.json`** (4,545 trains), **`SF-TRAINS.json`** (1,412 trains): Complete timetables and route stops for 8,490 trains comprising 170,340 route leg stops.
- **`india_railway_stations.csv` / `.parquet`**: 8,990 stations with coordinates, state, zone, junction flags, and route counts.
- **`Train_delay_Prediction.csv`**: 190 trip-level run delay logs.
- **`Railway_Scheduling_Data.xlsx`**: 100 scheduling records (speed, priority, route).

---

## 2. Machine Learning Capabilities

### Model 1: Train ETA Prediction (`ml/eta_model.py`)
- **Objective**: Predict remaining journey / travel time in minutes.
- **Algorithm**: `XGBoostRegressor` / `LightGBMRegressor`.
- **Primary Features**: `scheduled_travel_time_mins`, `distance_kms`, `remaining_distance`, `historical_avg_delay`, `station_delay_rate`, `train_type_delay_rate`, `dwell_time_mins`, `is_junction`, `route_count`, `dep_hour`, `day_of_week`, `train_type`, `station_code`.

### Model 2: Train Delay Prediction & Propagation (`ml/delay_model.py`)
- **Objective**: Predict arrival/departure delay in minutes and estimate downstream propagation along future scheduled stops.
- **Algorithm**: `XGBoostRegressor` + Schedule-based propagation estimator.
- **Propagation Logic**: Combines ML station delay predictions with route leg attenuation/accumulation factors across downstream stops.

### Model 3: Traffic Conflict / Risk Prediction (`ml/conflict_model.py`)
- **Objective**: Identify timetable overlap risks and classify traffic conflict probability at station/track bottlenecks.
- **Algorithm**: `XGBoostClassifier` (Predicts `conflict_probability` and risk levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Fallback**: Schedule-based timetable conflict risk calculation engine when ML input is unavailable.

---

## 3. Directory Layout

```
ml/
├── data_loader.py            # Multi-format data loader (CSV, JSON, XLSX, Parquet)
├── data_validator.py          # Automated quality & health validation suite
├── preprocessing.py           # scikit-learn Pipeline & ColumnTransformer builder
├── feature_engineering.py     # Route leg extraction & dataset fusion engine
├── eta_model.py               # Model 1: ETA Prediction Model
├── delay_model.py             # Model 2: Delay & Downstream Propagation Model
├── conflict_model.py          # Model 3: Traffic Conflict Classification Model
├── prediction_service.py     # High-level unified prediction interface
├── prediction_api.py         # FastAPI REST service & OpenAPI docs
├── model_registry.py         # Joblib artifact loader, metadata & version registry
├── digital_twin_adapter.py   # Ingestion adapter for Digital Twin states
├── config.py                 # Hyperparameters, directories, and server options
└── schemas.py                # Pydantic request/response schemas

scripts/
├── train_all.py              # End-to-end model training orchestration script
├── evaluate_all.py           # Model evaluation & plot generation script
└── demo.py                   # Interactive CLI demonstration using real dataset

reports/
├── data_quality_report.json  # Data health validation results in JSON
├── data_quality_report.md    # Data health validation report in Markdown
├── eta_metrics.json          # ETA model evaluation metrics
├── delay_metrics.json        # Delay model evaluation metrics
├── conflict_metrics.json     # Conflict model evaluation metrics
├── feature_importance.json   # Top feature importances per model
└── plots/                    # High-resolution performance plots

tests/                        # Pytest automated test suite
```

---

## 4. Setup & Execution Commands

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train Models & Generate Joblib Artifacts
```bash
python scripts/train_all.py
```

### Step 3: Evaluate Models & Generate Visualization Plots
```bash
python scripts/evaluate_all.py
```

### Step 4: Run Interactive Terminal Demo
```bash
python scripts/demo.py
```

### Step 5: Start FastAPI Server
```bash
python -m uvicorn ml.prediction_api:app --reload
```
Interactive API documentation available at: `http://127.0.0.1:8000/docs`

---

## 5. Automated Testing
Run the complete unit & integration test suite:
```bash
pytest -v
```

---

## 6. Integration Specifications

### Digital Twin Adapter Interface (`ml/digital_twin_adapter.py`)
Parses real-time state dictionaries from the Digital Twin engine:
```json
{
  "timestamp": "2026-08-16T00:00:00Z",
  "trains": [
    {
      "train_id": "12673",
      "train_type": "Express",
      "station_code": "MAS",
      "delay_minutes": 10.0
    }
  ]
}
```

### OR-Tools Optimizer Payload Schema
Produces machine-readable output consumed directly by the OR-Tools optimization engine:
```json
{
  "train_id": "12673",
  "station_code": "MAS",
  "predicted_eta_minutes": 128.5,
  "predicted_delay_minutes": 14.2,
  "conflict_probability": 0.85,
  "risk_level": "CRITICAL",
  "priority_weight": 1.5
}
```

---

## 7. Limitations & Safety Disclaimer

1. **Static Historical Data**: The dataset provides historical static train schedules and delay statistics. It is not connected to real-time live GPS telemetry unless connected via the Digital Twin adapter.
2. **Decision-Support Scope**: This AI/ML engine operates purely as a decision-support module for railway controllers. Final signaling authority and physical interlock safety regulations reside outside the ML system.
