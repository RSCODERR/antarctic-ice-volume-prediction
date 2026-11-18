"""
Features router serving the 14-feature schema, descriptions, and regularized coefficients.
"""

from typing import List
from fastapi import APIRouter, Depends
from app.schemas.responses import FeatureItem
from app.services.data_service import DataService
from app.dependencies import get_data_service

router = APIRouter(prefix="/api/features", tags=["Features"])

@router.get("", response_model=List[FeatureItem])
def list_features(data_svc: DataService = Depends(get_data_service)):
    """Return the frozen 14-feature dictionary, mathematical definitions, and ElasticNet sparsity weights."""
    return data_svc.get_features()
