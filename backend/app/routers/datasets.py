"""
Datasets router serving metadata and inventory for cryosphere observation datasets.
"""

from typing import List
from fastapi import APIRouter, Depends
from app.schemas.responses import DatasetItem
from app.services.data_service import DataService
from app.dependencies import get_data_service

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

@router.get("", response_model=List[DatasetItem])
def list_datasets(data_svc: DataService = Depends(get_data_service)):
    """Return verified inventory of cryospheric observation, physical modeling, and ML datasets."""
    return data_svc.get_datasets()
