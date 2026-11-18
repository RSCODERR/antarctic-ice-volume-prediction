"""
Overview router providing project statistics and glaciological boundaries.
"""

from fastapi import APIRouter, Depends
from app.schemas.responses import OverviewResponse
from app.services.data_service import DataService
from app.dependencies import get_data_service

router = APIRouter(prefix="/api", tags=["Overview"])

@router.get("/overview", response_model=OverviewResponse)
def get_overview(data_svc: DataService = Depends(get_data_service)):
    """Return project metadata, geographic domain boundaries, and scientific disclosures."""
    return data_svc.get_overview()
