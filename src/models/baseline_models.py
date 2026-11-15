"""
Baseline Models: Persistence and Historical Basin Mean
======================================================
Implements benchmark baselines:
1. M0-Persistence: y_hat[b, t] = y[b, t-1]
2. M0-Mean: y_hat[b, t] = mean(y[b, train])
"""

import numpy as np
import pandas as pd

class BasinPersistenceModel:
    """
    M0 - Basin-Specific Persistence Baseline.
    Predicts: y_hat[b, t] = y[b, t-1] (the lag-1 target value).
    """
    def __init__(self, lag_feature_col="Target_Volume_Change_Lag1_km3_yr"):
        self.lag_feature_col = lag_feature_col
        self.name = "M0_Persistence"
        self.is_probabilistic = False

    def fit(self, X, y, sample_weight=None):
        # Persistence has no parameters to fit
        return self

    def predict(self, X, return_std=False):
        if isinstance(X, pd.DataFrame):
            preds = X[self.lag_feature_col].values.copy()
        else:
            # Assume first column is lag-1
            preds = X[:, 0].copy()
            
        if return_std:
            return preds, np.zeros_like(preds)
        return preds

class BasinHistoricalMeanModel:
    """
    M0 - Basin Historical-Mean Baseline.
    Predicts: y_hat[b, t] = mean(y[b, s]) for s in training fold.
    """
    def __init__(self, basin_id_col="Basin_ID"):
        self.basin_id_col = basin_id_col
        self.name = "M0_Historical_Mean"
        self.basin_means = {}
        self.global_mean = 0.0
        self.is_probabilistic = False

    def fit(self, X, y, sample_weight=None):
        if isinstance(X, pd.DataFrame) and self.basin_id_col in X.columns:
            basins = X[self.basin_id_col]
            for b in basins.unique():
                idx = (basins == b)
                self.basin_means[b] = float(np.mean(y[idx]))
        self.global_mean = float(np.mean(y))
        return self

    def predict(self, X, return_std=False):
        if isinstance(X, pd.DataFrame) and self.basin_id_col in X.columns:
            preds = np.array([self.basin_means.get(b, self.global_mean) for b in X[self.basin_id_col]])
        else:
            preds = np.full(len(X), self.global_mean)
            
        if return_std:
            return preds, np.zeros_like(preds)
        return preds

