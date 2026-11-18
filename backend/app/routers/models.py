"""
Models router serving evaluation metrics, comparisons, and individual model specifications.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.responses import ModelSummary, ModelDetailResponse
from app.services.data_service import DataService
from app.dependencies import get_data_service

router = APIRouter(prefix="/api/models", tags=["Models"])

@router.get("", response_model=List[ModelSummary])
def list_models(data_svc: DataService = Depends(get_data_service)):
    """Return all six evaluated candidate models, architectures, and evaluation metrics."""
    return data_svc.get_models_summary()

@router.get("/comparison", response_model=List[Dict[str, Any]])
def get_model_comparison(data_svc: DataService = Depends(get_data_service)):
    """Return raw comparison matrix data for all candidate models."""
    return data_svc.model_comparison

@router.get("/{model_id}", response_model=ModelDetailResponse)
def get_model_detail(model_id: str, data_svc: DataService = Depends(get_data_service)):
    """Return detailed metadata, per-basin performance, and feature importances for one model."""
    detail = data_svc.get_model_detail(model_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model identifier '{model_id}' not found. Supported IDs: MOD-01 to MOD-06, or model names."
        )
    return detail
