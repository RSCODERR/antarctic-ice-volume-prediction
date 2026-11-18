"""
Projections router for CryoPredict future projections (Stage 7.1/7.2).
Provides dedicated access to multi-decadal multi-quantile future trajectories
derived from the audited ISMIP6 multi-model archive.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.schemas.projection import (
    ScenarioItem,
    FutureModelInfoResponse,
    AvailabilityResponse,
    ProjectionTrajectoryResponse
)
from app.services.projection_service import ProjectionService
from app.dependencies import get_projection_service

router = APIRouter(prefix="/api/projections", tags=["Future Projections"])

@router.get("/scenarios", response_model=List[ScenarioItem])
def get_scenarios(
    proj_svc: ProjectionService = Depends(get_projection_service)
):
    """
    Return actual supported scenarios and their provenance.
    Distinguishes native ISMIP6 scenarios ('NATIVE_ISMIP6') from the pattern-scaled
    emulator synthesis ('SCALED_EMULATOR_SYNTHESIS') for SSP2-4.5.
    """
    return proj_svc.get_scenarios()

@router.get("/models", response_model=FutureModelInfoResponse)
def get_model_info(
    proj_svc: ProjectionService = Depends(get_projection_service)
):
    """
    Return QGB future projection emulator metadata, candidate model comparisons,
    Leave-One-Model-Family-Out (LOMFO) cross-validation results, and scientific notices.
    """
    return proj_svc.get_model_info()

@router.get("/availability", response_model=AvailabilityResponse)
def get_availability(
    proj_svc: ProjectionService = Depends(get_projection_service)
):
    """
    Return available years (2015-2100), spatial units (Hp-I, I-Ipp, Ipp-J, Domain_A),
    and scenario combinations from the actual projection manifest.
    """
    return proj_svc.get_availability()

@router.get("/trajectory", response_model=ProjectionTrajectoryResponse)
def get_trajectory(
    scenario: str = Query(..., description="Scenario identifier ('RCP8.5', 'RCP2.6', 'SSP2-4.5')"),
    spatial_unit: Optional[str] = Query(None, description="Spatial unit ('Hp-I', 'I-Ipp', 'Ipp-J', 'Domain_A')"),
    basin_id: Optional[str] = Query(None, description="Alias for spatial_unit"),
    start_year: Optional[int] = Query(2015, ge=2015, le=2100, description="Start year (default 2015)"),
    end_year: Optional[int] = Query(2100, ge=2015, le=2100, description="End year (default 2100)"),
    proj_svc: ProjectionService = Depends(get_projection_service)
):
    """
    Retrieve precomputed multi-quantile future trajectory for a scenario and spatial unit.
    The projection manifest is the authoritative source; no arbitrary unforced inference is run.
    """
    target_unit = spatial_unit or basin_id or "Domain_A"

    if start_year and end_year and start_year > end_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"start_year ({start_year}) cannot exceed end_year ({end_year})."
        )

    try:
        return proj_svc.get_trajectory(
            scenario=scenario,
            spatial_unit=target_unit,
            start_year=start_year,
            end_year=end_year
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
