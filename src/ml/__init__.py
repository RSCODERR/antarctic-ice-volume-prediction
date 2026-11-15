"""
ML module facade for Antarctic Ice Volume Prediction.
Exposes baseline and trained regression models from src.models.
"""

from src.models.baseline_models import BasinHistoricalMeanModel, BasinPersistenceModel
from src.models.linear_models import BayesianRidgeModel, ElasticNetModel
from src.models.tree_models import ShallowRandomForestModel, ConstrainedGradientBoostingModel

__all__ = [
    "BasinHistoricalMeanModel",
    "BasinPersistenceModel",
    "BayesianRidgeModel",
    "ElasticNetModel",
    "ShallowRandomForestModel",
    "ConstrainedGradientBoostingModel"
]
