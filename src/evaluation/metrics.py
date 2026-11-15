"""
Evaluation Metrics Module
=========================
Calculates point prediction, cumulative drift, and probabilistic calibration metrics.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

def calculate_point_metrics(y_true, y_pred):
    """
    Computes RMSE, MAE, Mean Bias, and R2.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    residuals = y_pred - y_true
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    mae = float(np.mean(np.abs(residuals)))
    bias = float(np.mean(residuals))
    
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_res = np.sum(residuals ** 2)
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-9 else 0.0
    
    return {
        "rmse": rmse,
        "mae": mae,
        "bias": bias,
        "r2": r2
    }

def calculate_gaussian_crps(y_true, mu, sigma):
    """
    Computes analytical Continuous Ranked Probability Score (CRPS)
    for Gaussian predictive distributions: N(mu, sigma^2).
    """
    y_true = np.asarray(y_true)
    mu = np.asarray(mu)
    sigma = np.asarray(sigma)
    
    # Avoid zero division
    sigma = np.maximum(sigma, 1e-6)
    z = (y_true - mu) / sigma
    
    # CRPS = sigma * [ z * (2*Phi(z) - 1) + 2*phi(z) - 1/sqrt(pi) ]
    crps = sigma * (z * (2.0 * norm.cdf(z) - 1.0) + 2.0 * norm.pdf(z) - 1.0 / np.sqrt(np.pi))
    return float(np.mean(crps))

def calculate_probabilistic_calibration(y_true, y_pred, y_std, confidence=0.95):
    """
    Computes empirical coverage probability, mean interval width, and CRPS.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    y_std = np.asarray(y_std)
    
    z_crit = norm.ppf(0.5 + confidence / 2.0)  # 1.95996 for 95%
    lower = y_pred - z_crit * y_std
    upper = y_pred + z_crit * y_std
    
    inside = (y_true >= lower) & (y_true <= upper)
    coverage = float(np.mean(inside))
    sharpness = float(np.mean(upper - lower))
    crps = calculate_gaussian_crps(y_true, y_pred, y_std)
    
    return {
        "coverage_95": coverage,
        "mean_interval_width": sharpness,
        "crps": crps
    }

