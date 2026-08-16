# SIH25022 Railway Digital Twin Backend

A prototype backend for SIH 2025 PS SIH25022:
**Maximizing Section Throughput Using AI-Powered Precise Train Traffic Control**

The backend implements:

- Railway digital-twin state model
- Synthetic railway network and train timetable
- Discrete-time train simulator
- Synthetic disruption generation
- Delay prediction ML model
- OR-Tools conflict-free sequencing optimizer
- What-if scenario simulation
- FastAPI REST API

## Important

This is a prototype. The included telemetry/training data is synthetic and must not be presented as real Indian Railways telemetry.

## Architecture

Client
  -> FastAPI
  -> Digital Twin state
  -> ML prediction
  -> OR-Tools optimization
  -> What-if simulation

## Run

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

The first request to `/ml/train` creates a synthetic training set and trains the delay model.

## Main endpoints

GET  /health
GET  /network
GET  /trains
GET  /state
POST /ml/train
POST /ml/predict-delay
POST /simulation/reset
POST /simulation/step
POST /simulation/scenario
POST /optimization/sequence
POST /optimization/recommend
GET  /metrics

## Example

Train the model:

```bash
curl -X POST http://127.0.0.1:8000/ml/train
```

Predict delay:

```bash
curl -X POST http://127.0.0.1:8000/ml/predict-delay \
  -H "Content-Type: application/json" \
  -d "{\"train_id\":\"T101\"}"
```

Generate a 15-minute delay scenario:

```bash
curl -X POST http://127.0.0.1:8000/simulation/scenario \
  -H "Content-Type: application/json" \
  -d "{\"train_id\":\"T101\",\"delay_minutes\":15,\"horizon_minutes\":30}"
```

Get an optimized sequence:

```bash
curl -X POST http://127.0.0.1:8000/optimization/recommend \
  -H "Content-Type: application/json" \
  -d "{\"block_id\":\"B03\"}"
```