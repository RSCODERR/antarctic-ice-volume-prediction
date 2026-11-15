"""
Data module facade for Antarctic Ice Volume Prediction.
Provides utilities for accessing raw, processed, and feature datasets.
"""

import os
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_ml_dataset() -> pd.DataFrame:
    """Load the frozen Stage 6.0 ML dataset."""
    path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_ml_dataset.csv')
    return pd.read_csv(path)

def get_temporal_splits() -> pd.DataFrame:
    """Load the frozen Stage 6.0 temporal split manifest."""
    path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_temporal_split_manifest.csv')
    return pd.read_csv(path)

def get_feature_dictionary() -> pd.DataFrame:
    """Load the feature dictionary."""
    path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_feature_dictionary.csv')
    return pd.read_csv(path)
