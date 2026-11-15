"""
Linear Models: Bayesian Ridge and ElasticNet
============================================
Primary linear benchmark candidates for Antarctic Peninsula ice volume prediction:
1. M2 - Bayesian Ridge Regression (Probabilistic Linear)
2. M3 - ElasticNet Regression (Regularized Point Prediction)
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import BayesianRidge, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

class BayesianRidgeModel:
    """
    M2 - Bayesian Ridge Regression.
    Primary probabilistic linear candidate.
    
    Likelihood: y ~ N(X w, lambda^-1 I)
    Prior:      w ~ N(0, alpha^-1 I)
    Predictive: y_pred ~ N(x^T w_map, 1/lambda + x^T Sigma_w x)
    """
    def __init__(self, feature_cols, compute_score=True):
        self.feature_cols = feature_cols
        self.name = "M2_Bayesian_Ridge"
        self.is_probabilistic = True
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.model = BayesianRidge(compute_score=compute_score)
        self.fitted = False

    def fit(self, X, y, sample_weight=None):
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.fit_transform(X_sub)
        X_scale = self.scaler.fit_transform(X_imp)
        
        # Fit Bayesian Ridge with optional sample weights
        if sample_weight is not None:
            self.model.fit(X_scale, y, sample_weight=sample_weight)
        else:
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

class ElasticNetModel:
    """
    M3 - ElasticNet Regression.
    Primary regularized point-prediction candidate.
    
    Penalized objective:
    min_w (1 / 2N) ||y - X w||^2 + alpha * l1_ratio * ||w||_1 + 0.5 * alpha * (1 - l1_ratio) * ||w||_2^2
    Tuning conducted strictly inside training fold using 3-fold cross validation.
    """
    def __init__(self, feature_cols, l1_ratios=None, cv=3, random_state=42):
        self.feature_cols = feature_cols
        self.name = "M3_ElasticNet"
        self.is_probabilistic = False
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        if l1_ratios is None:
            l1_ratios = [0.1, 0.5, 0.7, 0.9, 0.99]
        self.model = ElasticNetCV(l1_ratio=l1_ratios, cv=cv, random_state=random_state, max_iter=3000)
        self.fitted = False

    def fit(self, X, y, sample_weight=None):
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.fit_transform(X_sub)
        X_scale = self.scaler.fit_transform(X_imp)
        
        if sample_weight is not None:
            self.model.fit(X_scale, y, sample_weight=sample_weight)
        else:
            self.model.fit(X_scale, y)
            
        self.fitted = True
        return self

    def predict(self, X, return_std=False):
        assert self.fitted, "Model must be fitted before predict"
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.transform(X_sub)
        X_scale = self.scaler.transform(X_imp)
        
        preds = self.model.predict(X_scale)
        if return_std:
            return preds, np.zeros_like(preds)
        return preds

