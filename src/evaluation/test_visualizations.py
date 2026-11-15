"""
Diagnostic Visualization Engine for Phase 4C Test Evaluation
============================================================
Generates the 6 scientific figures for held-out test evaluation:
1. fig7_test_observed_vs_predicted_annual_volume.png
2. fig8_test_basin_specific_trajectories.png
3. fig9_test_cumulative_volume_trajectories.png
4. fig10_test_basin_specific_residuals.png
5. fig11_test_year_blocked_errors.png
6. fig12_test_prediction_interval_calibration.png
"""

import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

ARTIFACT_DIR = r"C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f\figures"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Matplotlib styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial"],
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.2,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "figure.titlesize": 13,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.dpi": 300
})

MODEL_COLORS = {
    "M0_Persistence": "#e66101",
    "M0_Historical_Mean": "#5e3c99",
    "M2_Bayesian_Ridge": "#2b83ba",
    "M2_Bayesian_Ridge_Weighted": "#1b7837",
    "M3_ElasticNet": "#fdae61",
    "M4_Random_Forest": "#7b3294",
    "M5_Gradient_Boosting": "#d7191c",
    "M6_Gaussian_Process": "#008837"
}

def generate_test_figures():
    print("=" * 80)
    print("PHASE 4C: GENERATING SCIENTIFIC EVALUATION FIGURES")
    print("=" * 80)
    
    # Load test predictions
    preds_df = pd.read_csv(os.path.join(TABLES_DIR, "test_predictions.csv"))
    metrics_pooled = pd.read_csv(os.path.join(TABLES_DIR, "test_metrics_pooled.csv"))
    metrics_basin = pd.read_csv(os.path.join(TABLES_DIR, "test_metrics_by_basin.csv"))
    
    phys_preds = preds_df[preds_df["Basin_ID"] != "Domain_A"].copy()
    
    # -------------------------------------------------------------------------
    # FIGURE 7: Observed vs. Predicted Annual Volume Change
    # -------------------------------------------------------------------------
    print("Generating Figure 7: Observed vs. Predicted Annual Volume Change...")
    fig, axes = plt.subplots(2, 4, figsize=(18, 9), sharex=True, sharey=True)
    axes = axes.flatten()
    
    models = [
        "M0_Persistence", "M0_Historical_Mean", "M2_Bayesian_Ridge", "M2_Bayesian_Ridge_Weighted",
        "M3_ElasticNet", "M4_Random_Forest", "M5_Gradient_Boosting", "M6_Gaussian_Process"
    ]
    
    basin_markers = {"Hp-I": "o", "I-Ipp": "s", "Ipp-J": "^"}
    basin_colors = {"Hp-I": "#1f77b4", "I-Ipp": "#2ca02c", "Ipp-J": "#d62728"}
    
    for idx, model_name in enumerate(models):
        ax = axes[idx]
        sub = phys_preds[phys_preds["Model_Name"] == model_name]
        m_row = metrics_pooled[metrics_pooled["Model_Name"] == model_name].iloc[0]
        
        # 1:1 Reference Line
        ax.plot([-50, 20], [-50, 20], color="#888888", linestyle="--", linewidth=1.2, zorder=1)
        ax.axhline(0, color="#cccccc", linestyle=":", linewidth=0.8)
        ax.axvline(0, color="#cccccc", linestyle=":", linewidth=0.8)
        
        for b_id in ["Hp-I", "I-Ipp", "Ipp-J"]:
            b_sub = sub[sub["Basin_ID"] == b_id]
            ax.scatter(
                b_sub["y_true"], b_sub["y_pred"],
                color=basin_colors[b_id], marker=basin_markers[b_id],
                s=45, alpha=0.85, edgecolors="k", linewidth=0.6,
                label=b_id if idx == 0 else None, zorder=3
            )
            
        ax.set_title(f"{model_name}\nRMSE={m_row['RMSE_km3_yr']:.2f} | MAE={m_row['MAE_km3_yr']:.2f} | Bias={m_row['Mean_Bias_km3_yr']:+.2f}", fontsize=9.5)
        ax.grid(True, linestyle="--", alpha=0.6)
        if idx >= 4:
            ax.set_xlabel("Reconstructed Target ($km^3/yr$)", fontsize=9.5)
        if idx % 4 == 0:
            ax.set_ylabel("Predicted Rate ($km^3/yr$)", fontsize=9.5)
        ax.set_xlim(-45, 15)
        ax.set_ylim(-45, 15)
        
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 0.98), ncol=3, frameon=True, fontsize=10)
    fig.suptitle("Figure 7: Phase 4C Held-Out Test (2016–2024) — Observed vs. Predicted Annual Volume Change", y=1.02, fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig7_path = os.path.join(FIGURES_DIR, "fig7_test_observed_vs_predicted_annual_volume.png")
    fig.savefig(fig7_path, bbox_inches="tight", dpi=300)
    shutil.copy(fig7_path, os.path.join(ARTIFACT_DIR, "fig7_test_observed_vs_predicted_annual_volume.png"))
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 8: Basin-Specific 2016–2024 Time Series Trajectories
    # -------------------------------------------------------------------------
    print("Generating Figure 8: Basin-Specific Test Trajectories...")
    fig, axes = plt.subplots(4, 1, figsize=(14, 14), sharex=True)
    basins = ["Hp-I", "I-Ipp", "Ipp-J", "Domain_A"]
    basin_titles = [
        "Basin Hp-I (Palmer Land / Southern Peninsula)",
        "Basin I-Ipp (Graham Land West)",
        "Basin Ipp-J (Graham Land East / Larsen Coast)",
        "Domain A (Mainland Peninsula Aggregate)"
    ]
    
    highlight_models = ["M0_Historical_Mean", "M0_Persistence", "M2_Bayesian_Ridge_Weighted", "M5_Gradient_Boosting"]
    
    for b_idx, b_id in enumerate(basins):
        ax = axes[b_idx]
        b_sub = preds_df[(preds_df["Basin_ID"] == b_id) & (preds_df["Model_Name"] == "M0_Historical_Mean")].sort_values("Evaluation_Year")
        years = b_sub["Evaluation_Year"].values
        y_true = b_sub["y_true"].values
        
        # Plot true target
        ax.plot(years, y_true, color="#000000", linewidth=2.4, marker="o", markersize=6, label="Reconstructed Target", zorder=5)
        
        # Plot candidate models
        for m_name in highlight_models:
            m_sub = preds_df[(preds_df["Basin_ID"] == b_id) & (preds_df["Model_Name"] == m_name)].sort_values("Evaluation_Year")
            ax.plot(
                years, m_sub["y_pred"].values,
                color=MODEL_COLORS[m_name], linewidth=1.6, linestyle="--" if "M0" in m_name else "-",
                marker="x" if "M0" in m_name else ".", markersize=5,
                label=m_name, zorder=4
            )
            
        ax.set_title(basin_titles[b_idx], fontsize=11, fontweight="bold")
        ax.set_ylabel("Annual Rate ($km^3/yr$)", fontsize=9.5)
        ax.grid(True, linestyle="--", alpha=0.6)
        if b_idx == 0:
            ax.legend(loc="upper right", ncol=5, frameon=True, fontsize=8.5)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        
    axes[-1].set_xlabel("Calendar Year", fontsize=10.5)
    fig.suptitle("Figure 8: Phase 4C Test Trajectories (2016–2024) — Annual Grounded Volume Rates by Basin", y=0.995, fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig8_path = os.path.join(FIGURES_DIR, "fig8_test_basin_specific_trajectories.png")
    fig.savefig(fig8_path, bbox_inches="tight", dpi=300)
    shutil.copy(fig8_path, os.path.join(ARTIFACT_DIR, "fig8_test_basin_specific_trajectories.png"))
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 9: Cumulative Volume Trajectories & Endpoint Drift on Domain A
    # -------------------------------------------------------------------------
    print("Generating Figure 9: Cumulative Volume Trajectories on Domain A...")
    fig, ax = plt.subplots(figsize=(12, 7))
    
    dom_sub = preds_df[(preds_df["Basin_ID"] == "Domain_A") & (preds_df["Model_Name"] == "M0_Historical_Mean")].sort_values("Evaluation_Year")
    years = dom_sub["Evaluation_Year"].values
    true_cum = np.cumsum(dom_sub["y_true"].values)
    
    # Plot true cumulative trajectory
    ax.plot(years, true_cum, color="#000000", linewidth=3.0, marker="o", markersize=7, label=f"Reconstructed Truth (2024: {true_cum[-1]:.1f} km³)", zorder=6)
    
    for m_name in models:
        m_sub = preds_df[(preds_df["Basin_ID"] == "Domain_A") & (preds_df["Model_Name"] == m_name)].sort_values("Evaluation_Year")
        pred_cum = np.cumsum(m_sub["y_pred"].values)
        drift = pred_cum[-1] - true_cum[-1]
        
        ax.plot(
            years, pred_cum,
            color=MODEL_COLORS[m_name], linewidth=1.8,
            linestyle="--" if "M0" in m_name else "-",
            label=f"{m_name} (Drift: {drift:+.1f} km³)",
            zorder=4
        )
        
    ax.set_title("Figure 9: Phase 4C Cumulative Grounded Ice Loss (2016–2024) on Domain A", fontsize=12, fontweight="bold")
    ax.set_xlabel("Calendar Year", fontsize=10.5)
    ax.set_ylabel("Cumulative Volume Anomaly ($\Delta V$, $km^3$)", fontsize=10.5)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="lower left", frameon=True, fontsize=8.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    
    plt.tight_layout()
    fig9_path = os.path.join(FIGURES_DIR, "fig9_test_cumulative_volume_trajectories.png")
    fig.savefig(fig9_path, bbox_inches="tight", dpi=300)
    shutil.copy(fig9_path, os.path.join(ARTIFACT_DIR, "fig9_test_cumulative_volume_trajectories.png"))
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 10: Basin-Specific Residual Distributions
    # -------------------------------------------------------------------------
    print("Generating Figure 10: Basin-Specific Residuals...")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    basins_eval = ["Hp-I", "I-Ipp", "Ipp-J"]
    
    for b_idx, b_id in enumerate(basins_eval):
        ax = axes[b_idx]
        b_preds = phys_preds[phys_preds["Basin_ID"] == b_id]
        
        res_data = [b_preds[b_preds["Model_Name"] == m]["Residual"].values for m in models]
        
        bp = ax.boxplot(res_data, patch_artist=True, tick_labels=[m.replace("M2_", "").replace("M0_", "").replace("M_", "") for m in models])
        
        for patch, m in zip(bp['boxes'], models):
            patch.set_facecolor(MODEL_COLORS[m])
            patch.set_alpha(0.7)
            
        ax.axhline(0, color="k", linestyle="--", linewidth=1.0)
        ax.set_title(f"Basin {b_id} Residuals", fontsize=11, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.tick_params(axis='x', rotation=45)
        if b_idx == 0:
            ax.set_ylabel("Residual: $\hat{y} - y$ ($km^3/yr$)", fontsize=10)
            
    fig.suptitle("Figure 10: Phase 4C Residual Distributions Across Test Years (2016–2024)", y=1.02, fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig10_path = os.path.join(FIGURES_DIR, "fig10_test_basin_specific_residuals.png")
    fig.savefig(fig10_path, bbox_inches="tight", dpi=300)
    shutil.copy(fig10_path, os.path.join(ARTIFACT_DIR, "fig10_test_basin_specific_residuals.png"))
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 11: Annual Cluster RMSE Over Time
    # -------------------------------------------------------------------------
    print("Generating Figure 11: Annual Cluster Errors Over Time...")
    fig, ax = plt.subplots(figsize=(12, 6))
    yb_df = pd.read_csv(os.path.join(TABLES_DIR, "test_year_blocked_errors.csv"))
    
    for m in ["M0_Historical_Mean", "M0_Persistence", "M2_Bayesian_Ridge_Weighted", "M5_Gradient_Boosting"]:
        sub = yb_df[yb_df["Model_Name"] == m].sort_values("Evaluation_Year")
        ax.plot(
            sub["Evaluation_Year"], sub["Annual_Cluster_RMSE_km3_yr"],
            color=MODEL_COLORS[m], linewidth=2.0,
            marker="o", label=m
        )
        
    ax.set_title("Figure 11: Phase 4C Annual 3-Basin Cluster RMSE Evolution (2016–2024)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Calendar Year", fontsize=10.5)
    ax.set_ylabel("Annual Cluster RMSE ($km^3/yr$)", fontsize=10.5)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    
    plt.tight_layout()
    fig11_path = os.path.join(FIGURES_DIR, "fig11_test_year_blocked_errors.png")
    fig.savefig(fig11_path, bbox_inches="tight", dpi=300)
    shutil.copy(fig11_path, os.path.join(ARTIFACT_DIR, "fig11_test_year_blocked_errors.png"))
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 12: Prediction Interval Calibration
    # -------------------------------------------------------------------------
    print("Generating Figure 12: Prediction Interval Calibration...")
    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    
    for idx, b_id in enumerate(["Hp-I", "I-Ipp", "Ipp-J"]):
        ax = axes[idx]
        sub = preds_df[(preds_df["Basin_ID"] == b_id) & (preds_df["Model_Name"] == "M2_Bayesian_Ridge_Weighted")].sort_values("Evaluation_Year")
        years = sub["Evaluation_Year"].values
        y_true = sub["y_true"].values
        y_pred = sub["y_pred"].values
        y_std = sub["y_std"].values
        
        ax.plot(years, y_true, color="k", marker="o", linewidth=2.0, label="Reconstructed Truth", zorder=5)
        ax.plot(years, y_pred, color=MODEL_COLORS["M2_Bayesian_Ridge_Weighted"], marker=".", linewidth=1.8, label="Bayesian Ridge Weighted", zorder=4)
        
        # 95% Confidence Band
        ax.fill_between(
            years, y_pred - 1.96 * y_std, y_pred + 1.96 * y_std,
            color=MODEL_COLORS["M2_Bayesian_Ridge_Weighted"], alpha=0.22,
            label="95% Predictive Interval ($\pm 1.96\sigma$)", zorder=2
        )
        
        # Observation uncertainty band
        obs_sigma = sub["Observation_Uncertainty_sigma_km3_yr"].values
        ax.fill_between(
            years, y_true - 1.96 * obs_sigma, y_true + 1.96 * obs_sigma,
            color="#888888", alpha=0.12, linestyle=":",
            label="Observation Uncertainty ($\pm 1.96\sigma_{obs}$)", zorder=1
        )
        
        ax.set_title(f"Basin {b_id} (Mean Width: {np.mean(2*1.96*y_std):.1f} km³/yr | Coverage: {np.mean((y_true >= y_pred-1.96*y_std)&(y_true <= y_pred+1.96*y_std))*100:.0f}%)", fontsize=10.5, fontweight="bold")
        ax.set_ylabel("Annual Rate ($km^3/yr$)", fontsize=9.5)
        ax.grid(True, linestyle="--", alpha=0.6)
        if idx == 0:
            ax.legend(loc="upper right", ncol=4, frameon=True, fontsize=8)
            
    axes[-1].set_xlabel("Calendar Year", fontsize=10.5)
    axes[-1].xaxis.set_major_locator(ticker.MultipleLocator(1))
    fig.suptitle("Figure 12: Phase 4C Bayesian Ridge Weighted 95% Interval Calibration (2016–2024)", y=0.995, fontsize=12.5, fontweight="bold")
    plt.tight_layout()
    fig12_path = os.path.join(FIGURES_DIR, "fig12_test_prediction_interval_calibration.png")
    fig.savefig(fig12_path, bbox_inches="tight", dpi=300)
    shutil.copy(fig12_path, os.path.join(ARTIFACT_DIR, "fig12_test_prediction_interval_calibration.png"))
    plt.close()
    
    print("All 6 Phase 4C figures generated and archived successfully.")

if __name__ == "__main__":
    generate_test_figures()

