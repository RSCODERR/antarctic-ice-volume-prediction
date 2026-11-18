# CryoPredict API Backend

Production-minded Python FastAPI backend exposing verified Antarctic Peninsula ice-volume and mass-balance research results, glaciological metadata, and real-time inference using frozen machine-learning model artifacts.

---

## 1. Architecture Overview

CryoPredict is structured with clean separation of concerns, strict dependency injection, and comprehensive glaciological safeguards:

```
antarctic-ice-volume-prediction/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint, CORS, exception handling, lifespan
│   ├── config.py                # Pydantic Settings & environment variable configuration
│   ├── dependencies.py          # Reusable dependency injection providers
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py            # GET /api/health
│   │   ├── overview.py          # GET /api/overview
│   │   ├── models.py            # GET /api/models, /api/models/comparison, /api/models/{model_id}
│   │   ├── predictions.py       # GET /api/predictions/historical, POST /api/predictions/run
│   │   ├── datasets.py          # GET /api/datasets
│   │   └── features.py          # GET /api/features
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── responses.py         # Pydantic response models for catalog, models, overview
│   │   └── prediction.py        # 14-feature payload schema, inference request/response models
│   └── services/
│       ├── __init__.py
│       ├── data_service.py      # In-memory cached provider for website assets and CSV tables
│       ├── model_service.py     # Artifact loader & real scikit-learn model execution engine
│       └── prediction_service.py # Inference validation, dummy alignment & physical guardrails
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and synchronous test runner
│   ├── test_health.py           # Health and root endpoint tests
│   ├── test_overview.py         # Overview and domain geometry tests
│   ├── test_models.py           # Model catalog and detail tests
│   ├── test_predictions.py      # Historical timeseries and live inference tests
│   └── test_datasets_and_features.py # Catalog inventory and feature dictionary tests
├── requirements.txt             # Frozen backend dependencies
├── API_DOCUMENTATION.md         # Comprehensive OpenAPI endpoint documentation
├── IMPLEMENTATION_REPORT.md     # Engineering certification, audit, and benchmark report
└── README.md                    # Setup and operational instructions
```

---

## 2. Installation & Setup

### Prerequisites
- Python 3.10+ (tested with Python 3.12.5)
- Virtual environment (recommended)

### Installation
From the repository root or backend folder:

```bash
# Activate your existing repository virtual environment
source .venv/bin/activate       # On Linux/macOS
.venv\Scripts\activate          # On Windows (PowerShell: .venv\Scripts\Activate.ps1)

# Install backend dependencies
pip install -r backend/requirements.txt
```

---

## 3. Running the Server

Start the API server with Uvicorn:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or run from the repository root:
```bash
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Root Info:** `http://localhost:8000/`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **OpenAPI JSON Schema:** `http://localhost:8000/openapi.json`
- **Health Check:** `http://localhost:8000/api/health`

---

## 4. Configuration

All configuration settings are managed via `app/config.py` using typed environment variables with sensible research defaults:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `CRYOPREDICT_ENV` | `production` | Deployment environment (`development` / `production`) |
| `CRYOPREDICT_DEBUG` | `False` | Enables debug logging and verbose tracebacks |
| `CRYOPREDICT_CORS_ORIGINS` | `["http://localhost:3000", ...]` | Permitted CORS frontend origins |
| `CRYOPREDICT_REPO_ROOT` | Auto-detected repository root | Absolute path to research repository root |

---

## 5. Running Tests

The test suite runs with `pytest` and verifies health, overview, models, historical timeseries filtering, live inference on all 6 candidate models, feature validation, non-finite rejection, and 2100 forecast prevention:

```bash
# Run backend test suite
pytest backend/tests -v

# Run full project test suite (including research & physical modeling tests)
pytest tests backend/tests -q
```
