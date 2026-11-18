"""
CryoPredict FastAPI Application.
Production-minded scientific backend exposing Antarctic Peninsula cryospheric research
and verified machine-learning inference pipelines.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.model_service import model_service
from app.services.data_service import data_service
from app.services.projection_service import projection_service
from app.routers import health, overview, models, predictions, datasets, features, projections

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cryopredict")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler ensuring models and assets are loaded once at startup."""
    logger.info("Initializing CryoPredict Backend...")
    logger.info(f"Repository Root: {settings.PATH_REPO_ROOT}")
    logger.info(f"Models Directory: {settings.PATH_MODELS_DIR}")
    
    # Reload/verify services
    if not data_service.is_loaded:
        data_service.load_all_data()
    if not model_service.is_loaded:
        model_service.load_artifacts()
    if not projection_service.is_loaded:
        projection_service.load_data()
        
    logger.info("CryoPredict Backend initialization complete.")
    yield
    logger.info("CryoPredict Backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global safe exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. File system details are hidden for security."}
    )

# Include API Routers
app.include_router(health.router)
app.include_router(overview.router)
app.include_router(models.router)
app.include_router(predictions.router)
app.include_router(datasets.router)
app.include_router(features.router)
app.include_router(projections.router)

@app.get("/", tags=["Root"])
def root_endpoint():
    """Root entrypoint returning platform identity, API version, and documentation links."""
    return {
        "platform": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health": "/api/health",
        "overview": "/api/overview",
        "models": "/api/models",
        "projections": "/api/projections/availability",
        "scientific_notice": (
            "CryoPredict is an academic research platform for the Antarctic Peninsula. "
            "Historical ML models are basin-level annual predictors (1995-2020), NOT 2100 climate projection engines. "
            "Future projections (2015-2100) are served via dedicated multi-model quantile emulator endpoints."
        )
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
