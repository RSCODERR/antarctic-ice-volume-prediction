"""
Gaussian Process Regression: Low-Dimensional Exploratory Candidate
==================================================================
Implements M6 - Gaussian Process Regression:
1. Input dimension restricted to p <= 4 features.
2. Matérn kernel with lengthscale bounds [0.5, 5.0] years (or normalized equivalent).
3. Homoscedastic observation noise variance alpha anchored to annual rate variance.
4. Documents homoscedasticity and multi-output cross-basin limitations.
"""

import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel as C, WhiteKernel
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

class LowDimGaussianProcessModel:
    """
    M6 - Low-Dimensional Gaussian Process Regression.
    Optional exploratory probabilistic candidate.
    
    Configuration:
    - Input dimension: p <= 4 features
    - Kernel: ConstantKernel * Matern(nu=1.5, length_scale=1.5, length_scale_bounds=(0.2, 5.0))
    - Observation noise: alpha = fixed physical annual rate variance (~64.0 km6/yr2)
    - Limitations: Homoscedastic noise assumption; decoupled cross-basin outputs.
    """
    def __init__(self, feature_cols, alpha=64.0, length_scale=1.5, length_scale_bounds=(0.2, 5.0), random_state=42):
        assert len(feature_cols) <= 4, f"GPR input dimension p must be <= 4, found {len(feature_cols)}"
        self.feature_cols = feature_cols
        self.name = "M6_Gaussian_Process"
        self.is_probabilistic = True
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        
        # Kernel: C(1.0) * Matern(length_scale=length_scale, nu=1.5)
        kernel = C(1.0, (1e-2, 1e2)) * Matern(
            length_scale=length_scale,
            length_scale_bounds=length_scale_bounds,
            nu=1.5
        )
        self.model = GaussianProcessRegressor(
            kernel=kernel,
            alpha=alpha,
            n_restarts_optimizer=5,
            random_state=random_state,
            normalize_y=True
        )
        self.fitted = False

    def fit(self, X, y, sample_weight=None):
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.fit_transform(X_sub)
        X_scale = self.scaler.fit_transform(X_imp)
        
        # GPR fits on standardized features
        self.model.fit(X_scale, y)
        self.fitted = True
        return self

    def predict(self, X, return_std=False):
        assert self.fitted, "Model must be fitted before predict"
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.transform(X_sub)
        X_scale = self.scaler.transform(X_imp)
        
        if return_std:
            y_pred, y_std = self.model.predict(X_scale, return_std=True)
            return y_pred, y_std
        return self.model.predict(X_scale)

