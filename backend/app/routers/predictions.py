"""
Predictions router serving historical predictions and interactive live inference.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.schemas.responses import HistoricalPredictionItem
from app.schemas.prediction import InferenceRequest, InferenceResponse, HistoricalFeaturesResponse
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService
from app.dependencies import get_data_service, get_prediction_service

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.get("/historical", response_model=List[HistoricalPredictionItem])
def get_historical_predictions(
    basin_id: Optional[str] = Query(None, description="Filter by basin ('Hp-I', 'I-Ipp', 'Ipp-J')"),
    year: Optional[int] = Query(None, ge=1979, le=2024, description="Filter by calendar year (1979-2024)"),
    split_status: Optional[str] = Query(None, description="Filter by split ('TRAINING', 'VALIDATION', 'TEST', etc.)"),
    data_svc: DataService = Depends(get_data_service)
):
    """Serve the 46-year historical prediction manifest with filtering capabilities."""
    if basin_id and basin_id.upper() not in {"HP-I", "I-IPP", "IPP-J"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid basin_id '{basin_id}'. Allowed basins: 'Hp-I', 'I-Ipp', 'Ipp-J'."
        )
    return data_svc.get_historical_predictions(basin_id=basin_id, year=year, split_status=split_status)

@router.get("/historical-features", response_model=HistoricalFeaturesResponse)
@router.get("/historical/features", response_model=HistoricalFeaturesResponse)
def get_historical_features(
    basin_id: str = Query(..., description="Basin identifier ('Hp-I', 'I-Ipp', 'Ipp-J')"),
    year: int = Query(..., description="Historical calendar year (1979-2024)"),
    data_svc: DataService = Depends(get_data_service)
):
    """
    Retrieve legitimate antecedent 14-feature vector for a specific basin and historical year.
    Enforces strict temporal antecedent ordering (Lag-1 is t-1, Lag-2 is t-2, rolling SMB is [t-3, t-1]).
    Returns 404 if the year falls outside the observational record (1979-2024).
    """
    if basin_id.upper() not in {"HP-I", "I-IPP", "IPP-J"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid basin_id '{basin_id}'. Allowed basins: 'Hp-I', 'I-Ipp', 'Ipp-J'."
        )
    
    if year < 1979 or year > 2024:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Historical features are only available within the 1979-2024 observational record. "
                f"Year {year} is out of bounds. For hypothetical or unobserved scenarios, use Mode B (Manual Inference)."
            )
        )

    res = data_svc.get_historical_features(basin_id=basin_id, year=year)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historical feature record not found for basin '{basin_id}' and year {year}."
        )
    return res

@router.post("/run", response_model=InferenceResponse, status_code=status.HTTP_200_OK)
def run_prediction(
    request: InferenceRequest,
    prediction_svc: PredictionService = Depends(get_prediction_service)
):
    """
    Run live interactive inference using verified saved model artifacts.
    Accepts 14 features and returns predicted annual mass balance (Gt/yr) and volume change (km3/yr).
    Centennial projections (year >= 2100) are strictly rejected.
    """
    try:
        return prediction_svc.run_inference(request)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(re))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing model inference."
        )
