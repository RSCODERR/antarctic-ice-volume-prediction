"""
Tree Ensemble Models: Shallow Random Forest and Constrained Gradient Boosting
============================================================================
Exploratory non-linear candidates with strict complexity regularization:
1. M4 - Shallow Random Forest (max_depth <= 3, min_samples_leaf >= 6)
2. M5 - Constrained Gradient Boosting (max_depth <= 2, min_samples_leaf >= 6, lr=0.05)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer

class ShallowRandomForestModel:
    """
    M4 - Shallow Random Forest.
    Exploratory non-linear candidate with strict tree depth and leaf constraints
    to prevent overfitting on small sample sizes (N=48 to 105).
    """
    def __init__(self, feature_cols, max_depth=3, min_samples_leaf=6, n_estimators=100, random_state=42):
        self.feature_cols = feature_cols
        self.name = "M4_Random_Forest"
        self.is_probabilistic = False
        self.imputer = SimpleImputer(strategy="median")
        self.model = RandomForestRegressor(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.fitted = False

    def fit(self, X, y, sample_weight=None):
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.fit_transform(X_sub)
        
        if sample_weight is not None:
            self.model.fit(X_imp, y, sample_weight=sample_weight)
        else:
            self.model.fit(X_imp, y)
            
        self.fitted = True
        return self

    def predict(self, X, return_std=False):
        assert self.fitted, "Model must be fitted before predict"
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.transform(X_sub)
        
        preds = self.model.predict(X_imp)
        if return_std:
            # Tree ensemble variance across individual trees can serve as empirical spread
            tree_preds = np.array([tree.predict(X_imp) for tree in self.model.estimators_])
            std_preds = np.std(tree_preds, axis=0)
            return preds, std_preds
        return preds

class ConstrainedGradientBoostingModel:
    """
    M5 - Constrained Gradient Boosting.
    Optional exploratory candidate with conservative learning rate and shallow trees.
    """
    def __init__(self, feature_cols, max_depth=2, min_samples_leaf=6, learning_rate=0.05, n_estimators=50, subsample=0.8, random_state=42):
        self.feature_cols = feature_cols
        self.name = "M5_Gradient_Boosting"
        self.is_probabilistic = False
        self.imputer = SimpleImputer(strategy="median")
        self.model = GradientBoostingRegressor(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            learning_rate=learning_rate,
            n_estimators=n_estimators,
            subsample=subsample,
            random_state=random_state
        )
        self.fitted = False

    def fit(self, X, y, sample_weight=None):
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.fit_transform(X_sub)
        
        if sample_weight is not None:
            self.model.fit(X_imp, y, sample_weight=sample_weight)
        else:
            self.model.fit(X_imp, y)
            
        self.fitted = True
        return self

    def predict(self, X, return_std=False):
        assert self.fitted, "Model must be fitted before predict"
        X_sub = X[self.feature_cols].values if isinstance(X, pd.DataFrame) else X
        X_imp = self.imputer.transform(X_sub)
        
        preds = self.model.predict(X_imp)
        if return_std:
            return preds, np.zeros_like(preds)
        return preds

