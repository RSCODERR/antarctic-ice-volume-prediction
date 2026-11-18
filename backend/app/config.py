"""
Configuration module for CryoPredict FastAPI Backend.
Resolves repository paths, environment variables, and application settings.
"""

import os
from pathlib import Path
from typing import List

# Resolve base directories relative to repository root
DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = Path(os.getenv("CRYOPREDICT_REPO_ROOT", str(DEFAULT_REPO_ROOT)))

MODELS_DIR = REPO_ROOT / "models"
REPORTS_DIR = REPO_ROOT / "reports"
WEBSITE_ASSETS_DIR = REPORTS_DIR / "website_assets"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPO_ROOT / "figures"
DATA_DIR = REPO_ROOT / "data"
PROJECTIONS_DIR = DATA_DIR / "projections"
FUTURE_MODELS_DIR = MODELS_DIR / "stage7_1_future_models"

class Settings:
    APP_NAME: str = "CryoPredict API"
    APP_DESCRIPTION: str = (
        "Interactive scientific platform API for exploring Antarctic Peninsula "
        "ice-volume dynamics, 2D SSA physical modeling, and ML benchmarking."
    )
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    
    # Glaciological Constants
    SOLID_ICE_DENSITY_GT_KM3: float = 0.917  # 917 kg/m^3 -> Gt/km^3
    DOMAIN_AREA_KM2: float = 216062.17       # Grounded WGS84 area
    DOMAIN_VOLUME_KM3: float = 140702.51     # BedMachine solid ice volume
    
    # Drainage Basins
    BASINS: dict = {
        "Hp-I": {"name": "Palmer Land West", "area_km2": 108945.63},
        "I-Ipp": {"name": "Graham Land", "area_km2": 51993.42},
        "Ipp-J": {"name": "Palmer Land East", "area_km2": 55123.12}
    }
    
    # Path mappings
    PATH_REPO_ROOT: Path = REPO_ROOT
    PATH_MODELS_DIR: Path = MODELS_DIR
    PATH_FUTURE_MODELS_DIR: Path = FUTURE_MODELS_DIR
    PATH_WEBSITE_ASSETS: Path = WEBSITE_ASSETS_DIR
    PATH_TABLES: Path = TABLES_DIR
    PATH_FIGURES: Path = FIGURES_DIR
    PATH_PROJECTIONS_DIR: Path = PROJECTIONS_DIR
    PATH_PROJECTIONS_ORIGINAL_FILE: Path = PROJECTIONS_DIR / "stage7_1_future_projections_2015_2100.csv"
    PATH_PROJECTIONS_REARRANGED_FILE: Path = PROJECTIONS_DIR / "stage7_3_future_projections_rearranged_2015_2100.csv"
    PATH_PROJECTIONS_FILE: Path = PATH_PROJECTIONS_REARRANGED_FILE

settings = Settings()
