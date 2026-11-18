"""
FastAPI dependency injectors for CryoPredict services.
"""

from app.services.data_service import data_service, DataService
from app.services.model_service import model_service, ModelService
from app.services.prediction_service import prediction_service, PredictionService
from app.services.projection_service import projection_service, ProjectionService

def get_data_service() -> DataService:
    return data_service

def get_model_service() -> ModelService:
    return model_service

def get_prediction_service() -> PredictionService:
    return prediction_service

def get_projection_service() -> ProjectionService:
    return projection_service
