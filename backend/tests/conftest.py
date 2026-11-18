"""
Pytest fixtures and configuration for CryoPredict backend tests.
"""

import sys
import urllib.parse
from pathlib import Path
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

class MockResponse:
    """Synchronous test response object mirroring requests/httpx Response."""
    def __init__(self, status_code: int, data: any):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

def to_dict(obj):
    """Recursively converts Pydantic models or objects to plain Python dicts."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif isinstance(obj, list):
        return [to_dict(x) for x in obj]
    return obj

class TestApiClient:
    """
    Lightweight, synchronous API test client avoiding AnyIO blocking thread portal
    which can stall in isolated sandbox execution environments.
    """
    def get(self, path: str, params=None):
        parsed = urllib.parse.urlparse(path)
        route = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)
        if params:
            for k, v in params.items():
                query_params[k] = [str(v)]

        try:
            if route == "/":
                from app.main import root_endpoint
                return MockResponse(200, to_dict(root_endpoint()))
            elif route == "/api/health":
                from app.routers.health import get_health
                from app.dependencies import get_model_service
                res = get_health(model_svc=get_model_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/overview":
                from app.routers.overview import get_overview
                from app.dependencies import get_data_service
                res = get_overview(data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/models":
                from app.routers.models import list_models
                from app.dependencies import get_data_service
                res = list_models(data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/models/comparison":
                from app.routers.models import get_model_comparison
                from app.dependencies import get_data_service
                res = get_model_comparison(data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route.startswith("/api/models/"):
                model_id = route[len("/api/models/"):]
                from app.routers.models import get_model_detail
                from app.dependencies import get_data_service
                res = get_model_detail(model_id=model_id, data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/predictions/historical":
                from app.routers.predictions import get_historical_predictions
                from app.dependencies import get_data_service
                basin_id = query_params.get("basin_id", [None])[0]
                year_str = query_params.get("year", [None])[0]
                year = int(year_str) if year_str is not None else None
                split_status = query_params.get("split_status", [None])[0]
                res = get_historical_predictions(basin_id=basin_id, year=year, split_status=split_status, data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route in ("/api/predictions/historical-features", "/api/predictions/historical/features"):
                from app.routers.predictions import get_historical_features
                from app.dependencies import get_data_service
                basin_id = query_params.get("basin_id", [None])[0]
                year_str = query_params.get("year", [None])[0]
                if not basin_id or year_str is None:
                    return MockResponse(422, {"detail": "basin_id and year are required query parameters."})
                res = get_historical_features(basin_id=basin_id, year=int(year_str), data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/datasets":
                from app.routers.datasets import list_datasets
                from app.dependencies import get_data_service
                res = list_datasets(data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/features":
                from app.routers.features import list_features
                from app.dependencies import get_data_service
                res = list_features(data_svc=get_data_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/projections/scenarios":
                from app.routers.projections import get_scenarios
                from app.dependencies import get_projection_service
                res = get_scenarios(proj_svc=get_projection_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/projections/models":
                from app.routers.projections import get_model_info
                from app.dependencies import get_projection_service
                res = get_model_info(proj_svc=get_projection_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/projections/availability":
                from app.routers.projections import get_availability
                from app.dependencies import get_projection_service
                res = get_availability(proj_svc=get_projection_service())
                return MockResponse(200, to_dict(res))
            elif route == "/api/projections/trajectory":
                from app.routers.projections import get_trajectory
                from app.dependencies import get_projection_service
                scenario = query_params.get("scenario", [None])[0]
                spatial_unit = query_params.get("spatial_unit", [None])[0]
                basin_id = query_params.get("basin_id", [None])[0]
                s_yr_str = query_params.get("start_year", [None])[0]
                e_yr_str = query_params.get("end_year", [None])[0]
                s_yr = int(s_yr_str) if s_yr_str is not None else 2015
                e_yr = int(e_yr_str) if e_yr_str is not None else 2100
                if not scenario:
                    return MockResponse(422, {"detail": "scenario is required"})
                res = get_trajectory(
                    scenario=scenario,
                    spatial_unit=spatial_unit,
                    basin_id=basin_id,
                    start_year=s_yr,
                    end_year=e_yr,
                    proj_svc=get_projection_service()
                )
                return MockResponse(200, to_dict(res))
            else:
                return MockResponse(404, {"detail": "Not Found"})
        except HTTPException as he:
            return MockResponse(he.status_code, {"detail": he.detail})
        except ValidationError as ve:
            return MockResponse(422, {"detail": ve.errors()})
        except ValueError as ve:
            return MockResponse(400, {"detail": str(ve)})
        except Exception as e:
            return MockResponse(500, {"detail": str(e)})

    def post(self, path: str, json=None):
        parsed = urllib.parse.urlparse(path)
        route = parsed.path

        try:
            if route == "/api/predictions/run":
                from app.routers.predictions import run_prediction
                from app.dependencies import get_prediction_service
                from app.schemas.prediction import InferenceRequest
                try:
                    req = InferenceRequest(**(json or {}))
                except ValidationError as ve:
                    return MockResponse(422, {"detail": ve.errors()})
                except ValueError as ve:
                    return MockResponse(422, {"detail": str(ve)})
                res = run_prediction(request=req, prediction_svc=get_prediction_service())
                return MockResponse(200, to_dict(res))
            else:
                return MockResponse(404, {"detail": "Not Found"})
        except HTTPException as he:
            return MockResponse(he.status_code, {"detail": he.detail})
        except ValidationError as ve:
            return MockResponse(422, {"detail": ve.errors()})
        except ValueError as ve:
            return MockResponse(400, {"detail": str(ve)})
        except Exception as e:
            return MockResponse(500, {"detail": str(e)})

@pytest.fixture(scope="session")
def client():
    """Provides a TestApiClient session."""
    return TestApiClient()

@pytest.fixture(scope="session")
def sample_features():
    """Provides a valid 14-feature payload matching the Stage 6.0 schema."""
    return {
        "Target_Volume_Change_Lag1_km3_yr": -42.42,
        "Target_Volume_Change_Lag2_km3_yr": -4.09,
        "Net_MB_Lag1_Gt_yr": -3.76,
        "SMB_Lag1_Gt_yr": 67.24,
        "Discharge_Lag1_Gt_yr": 71.00,
        "SMB_Rolling3yr_Gt_yr": 68.50,
        "SMB_Anomaly_Lag1_Gt_yr": -1.26,
        "Grounded_Area_km2": 108945.63,
        "Mean_Baseline_Ice_Thickness_m": 1482.40,
        "Bed_Elevation_at_Gates_m": -124.20,
        "Driving_Stress_Index_kPa": 105.40,
        "is_Hp_I": 1.0,
        "is_I_Ipp": 0.0,
        "is_Ipp_J": 0.0
    }
