"""
Health Check router for CryoPredict API.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.schemas.responses import HealthResponse
from app.services.model_service import ModelService
from app.dependencies import get_model_service
from app.config import settings

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(model_svc: ModelService = Depends(get_model_service)):
    """Return backend health, API version, and model artifact loading status."""
    en_loaded = "elasticnet" in model_svc.models and model_svc.scaler is not None
    return HealthResponse(
        status="healthy" if en_loaded else "degraded",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment="production" if not settings.DEBUG else "development",
        models_loaded=model_svc.is_loaded,
        loaded_models_count=len(model_svc.models),
        primary_model_status="READY" if en_loaded else "MISSING"
    )
