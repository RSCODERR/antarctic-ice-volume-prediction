"""
Diagnostic Visualization Engine for Phase 4B
============================================
Generates the 6 required scientific evaluation figures:
1. fig1_observed_vs_predicted_annual_volume.png
2. fig2_basin_specific_oof_trajectories.png
3. fig3_oof_cumulative_volume_trajectories.png
4. fig4_basin_specific_residuals.png
5. fig5_year_blocked_errors.png
6. fig6_prediction_interval_calibration.png
"""

import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Artifacts directory for embedding
ARTIFACT_DIR = r"C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f\figures"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Matplotlib styling for high-quality publication output
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial"],
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.2,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "figure.titlesize": 14,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "figure.dpi": 300
})

MODEL_COLORS = {
    "M0_Persistence": "#e66101",
    "M0_Historical_Mean": "#999999",
    "M2_Bayesian_Ridge": "#5e3c99",
    "M2_Bayesian_Ridge_Weighted": "#2b83ba",
    "M3_ElasticNet": "#4dac26",
    "M4_Random_Forest": "#d7191c",
    "M5_Gradient_Boosting": "#fdae61",
    "M6_Gaussian_Process": "#1b7837"
}

def generate_all_figures():
    print("\n--- Generating Phase 4B Diagnostic Evaluation Figures ---")
    
    oof_path = os.path.join(TABLES_DIR, "oof_predictions.csv")
    yb_path = os.path.join(TABLES_DIR, "oof_year_blocked_errors.csv")
    pi_path = os.path.join(TABLES_DIR, "oof_prediction_intervals.csv")
    
    oof_df = pd.read_csv(oof_path)
    yb_df = pd.read_csv(yb_path)
    pi_df = pd.read_csv(pi_path)
    
    # -------------------------------------------------------------
    # Figure 1: Observed vs Predicted Annual Volume Changes
    # -------------------------------------------------------------
    print("Generating Figure 1: Observed vs Predicted Annual Volume Changes...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    basins = [("Hp-I", axes[0, 0]), ("I-Ipp", axes[0, 1]), ("Ipp-J", axes[1, 0]), ("Domain_A", axes[1, 1])]
    
    models_to_plot = ["M0_Persistence", "M0_Historical_Mean", "M2_Bayesian_Ridge_Weighted", "M3_ElasticNet", "M4_Random_Forest"]
    
    for b_id, ax in basins:
        b_data = oof_df[oof_df["Basin_ID"] == b_id]
        
        # 1:1 diagonal line
        all_vals = np.concatenate([b_data["y_true"].values, b_data["y_pred"].values])
        vmin, vmax = np.min(all_vals) - 5, np.max(all_vals) + 5
        ax.plot([vmin, vmax], [vmin, vmax], "k--", alpha=0.6, label="1:1 Perfect Agreement")
        
        for m_name in models_to_plot:
            m_sub = b_data[b_data["Model_Name"] == m_name]
            ax.scatter(m_sub["y_true"], m_sub["y_pred"], color=MODEL_COLORS.get(m_name, "black"),
                       label=m_name.replace("_", " "), alpha=0.7, s=35)
                       
        ax.set_title(f"Basin: {b_id}" if b_id != "Domain_A" else "Domain A Aggregate (Exact Sum)")
        ax.set_xlabel("Observed Volume Change (km³/yr)")
        ax.set_ylabel("Predicted Volume Change (km³/yr)")
        ax.grid(True)
        ax.set_xlim(vmin, vmax)
        ax.set_ylim(vmin, vmax)
        if b_id == "Hp-I":
            ax.legend(loc="upper left", frameon=True, fontsize=8)
            
    fig.suptitle("Out-of-Fold Evaluation: Observed vs. Predicted Annual Volume Change (1995–2014)", fontsize=14, y=0.98)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "fig1_observed_vs_predicted_annual_volume.png")
    fig.savefig(fig1_path, dpi=300)
    plt.close(fig)
    shutil.copy(fig1_path, os.path.join(ARTIFACT_DIR, "fig1_observed_vs_predicted_annual_volume.png"))
    
    # -------------------------------------------------------------
    # Figure 2: Basin-Specific OOF Trajectories (Annual Rates)
    # -------------------------------------------------------------
    print("Generating Figure 2: Basin-Specific Annual OOF Trajectories...")
    fig, axes = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
    basins_list = ["Hp-I", "I-Ipp", "Ipp-J"]
    
    for idx, b_id in enumerate(basins_list):
        ax = axes[idx]
        b_data = oof_df[oof_df["Basin_ID"] == b_id]
        
        # Ground truth
        truth = b_data[b_data["Model_Name"] == "M0_Persistence"].sort_values("Validation_Year")
        years = truth["Validation_Year"].values
        y_true = truth["y_true"].values
        sigma = truth["Observation_Uncertainty_sigma_km3_yr"].values
        
        # Plot truth + uncertainty band
        ax.plot(years, y_true, "k-o", linewidth=2.0, markersize=5, label="Observed Reconstruction", zorder=5)
        ax.fill_between(years, y_true - sigma, y_true + sigma, color="#cccccc", alpha=0.4, label="±1σ Annual Observation Uncertainty")
        
        # Plot model predictions
        for m_name in ["M0_Persistence", "M0_Historical_Mean", "M2_Bayesian_Ridge_Weighted", "M4_Random_Forest"]:
            m_sub = b_data[b_data["Model_Name"] == m_name].sort_values("Validation_Year")
            ax.plot(years, m_sub["y_pred"].values, linestyle="--", linewidth=1.8,
                    color=MODEL_COLORS[m_name], label=m_name.replace("_", " "))
                    
        ax.set_title(f"Basin {b_id} Out-of-Fold Annual Rate Trajectory (1995–2014)")
        ax.set_ylabel("Volume Rate (km³/yr)")
        ax.grid(True)
        ax.axhline(0, color="gray", linestyle=":", alpha=0.6)
        if idx == 0:
            ax.legend(loc="lower left", frameon=True, ncol=2, fontsize=8)
            
    axes[-1].set_xlabel("Validation Year")
    axes[-1].set_xticks(range(1995, 2015))
    fig.suptitle("Out-of-Fold Historical Trajectory Tracking Across Antarctic Peninsula Basins", fontsize=14, y=0.99)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "fig2_basin_specific_oof_trajectories.png")
    fig.savefig(fig2_path, dpi=300)
    plt.close(fig)
    shutil.copy(fig2_path, os.path.join(ARTIFACT_DIR, "fig2_basin_specific_oof_trajectories.png"))
    
    # -------------------------------------------------------------
    # Figure 3: Cumulative Volume Anomaly Trajectories (Drift)
    # -------------------------------------------------------------
    print("Generating Figure 3: OOF Cumulative Volume Change Trajectories...")
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    panels = [("Hp-I", axes[0, 0]), ("I-Ipp", axes[0, 1]), ("Ipp-J", axes[1, 0]), ("Domain_A", axes[1, 1])]
    
    for b_id, ax in panels:
        b_data = oof_df[oof_df["Basin_ID"] == b_id]
        
        # Ground truth cumulative
        truth = b_data[b_data["Model_Name"] == "M0_Persistence"].sort_values("Validation_Year")
        years = truth["Validation_Year"].values
        cum_true = np.cumsum(truth["y_true"].values)
        
        ax.plot(years, cum_true, "k-", linewidth=2.5, label="Observed Cumulative ΔV", zorder=5)
        
        for m_name in ["M0_Persistence", "M0_Historical_Mean", "M2_Bayesian_Ridge_Weighted", "M3_ElasticNet", "M4_Random_Forest"]:
            m_sub = b_data[b_data["Model_Name"] == m_name].sort_values("Validation_Year")
            cum_pred = np.cumsum(m_sub["y_pred"].values)
            ax.plot(years, cum_pred, linestyle="--", linewidth=1.6,
                    color=MODEL_COLORS[m_name], label=m_name.replace("_", " "))
                    
        ax.set_title(f"Cumulative Anomaly: {b_id}" if b_id != "Domain_A" else "Domain A Cumulative Loss (Exact Sum)")
        ax.set_ylabel("Cumulative ΔV (km³)")
        ax.grid(True)
        if b_id == "Domain_A":
            ax.legend(loc="lower left", frameon=True, fontsize=8)
            
    for ax in axes.flat:
        ax.set_xlabel("Validation Year")
        ax.set_xticks(range(1995, 2015, 2))
        
    fig.suptitle("Cumulative Volume Trajectory and Drift Over 20 Out-of-Fold Validation Years (1995–2014)", fontsize=14, y=0.98)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "fig3_oof_cumulative_volume_trajectories.png")
    fig.savefig(fig3_path, dpi=300)
    plt.close(fig)
    shutil.copy(fig3_path, os.path.join(ARTIFACT_DIR, "fig3_oof_cumulative_volume_trajectories.png"))
    
    # -------------------------------------------------------------
    # Figure 4: Basin-Specific Residuals Over Time
    # -------------------------------------------------------------
    print("Generating Figure 4: Basin-Specific Residual Plots...")
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    for idx, b_id in enumerate(basins_list):
        ax = axes[idx]
        b_data = oof_df[oof_df["Basin_ID"] == b_id]
        
        years = b_data[b_data["Model_Name"] == "M0_Persistence"].sort_values("Validation_Year")["Validation_Year"].values
        
        for m_name in ["M0_Persistence", "M0_Historical_Mean", "M2_Bayesian_Ridge_Weighted", "M4_Random_Forest"]:
            m_sub = b_data[b_data["Model_Name"] == m_name].sort_values("Validation_Year")
            residuals = m_sub["Residual"].values
            ax.plot(years, residuals, "-o", markersize=4, linewidth=1.5,
                    color=MODEL_COLORS[m_name], label=m_name.replace("_", " "))
                    
        ax.axhline(0, color="black", linestyle="-", linewidth=1.0)
        ax.set_title(f"Basin {b_id} Residuals (Predicted − Observed)")
        ax.set_ylabel("Residual (km³/yr)")
        ax.grid(True)
        if idx == 0:
            ax.legend(loc="upper left", frameon=True, ncol=2, fontsize=8)
            
    axes[-1].set_xlabel("Validation Year")
    axes[-1].set_xticks(range(1995, 2015))
    fig.suptitle("Temporal Residual Distribution: Highlighting Post-2002 Larsen B Dynamic Shift in Ipp-J", fontsize=14, y=0.99)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "fig4_basin_specific_residuals.png")
    fig.savefig(fig4_path, dpi=300)
    plt.close(fig)
    shutil.copy(fig4_path, os.path.join(ARTIFACT_DIR, "fig4_basin_specific_residuals.png"))
    
    # -------------------------------------------------------------
    # Figure 5: Year-Blocked Error Comparison (L2 Norm & Domain A Mass)
    # -------------------------------------------------------------
    print("Generating Figure 5: Year-Blocked Error Comparison...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
    
    models_compare = ["M0_Persistence", "M0_Historical_Mean", "M2_Bayesian_Ridge_Weighted", "M4_Random_Forest"]
    years = yb_df[yb_df["Model_Name"] == "M0_Persistence"]["Validation_Year"].values
    
    for m_name in models_compare:
        sub = yb_df[yb_df["Model_Name"] == m_name].sort_values("Validation_Year")
        ax1.plot(years, sub["Euclidean_Norm_L2"].values, "-o", markersize=5, linewidth=1.8,
                 color=MODEL_COLORS[m_name], label=m_name.replace("_", " "))
        ax2.plot(years, sub["Domain_A_Mass_Error"].values, "-s", markersize=5, linewidth=1.8,
                 color=MODEL_COLORS[m_name], label=m_name.replace("_", " "))
                 
    ax1.set_title("Year-Blocked Error Vector Euclidean Norm: ||e_t||₂ = √(e_{Hp-I}² + e_{I-Ipp}² + e_{Ipp-J}²)")
    ax1.set_ylabel("Error Norm (km³/yr)")
    ax1.grid(True)
    ax1.legend(loc="upper right", frameon=True, fontsize=8)
    
    ax2.axhline(0, color="black", linestyle="-", linewidth=1.0)
    ax2.set_title("Domain A Regional Mass Balance Error: e_{DomainA, t} = Σ_b (ŷ_{b,t} − y_{b,t})")
    ax2.set_ylabel("Aggregate Error (km³/yr)")
    ax2.grid(True)
    ax2.set_xlabel("Validation Year")
    ax2.set_xticks(range(1995, 2015))
    
    fig.suptitle("Contemporaneous Multi-Basin Response to Climate Events (1998 ENSO, 2002 Larsen B Collapse)", fontsize=14, y=0.98)
    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "fig5_year_blocked_errors.png")
    fig.savefig(fig5_path, dpi=300)
    plt.close(fig)
    shutil.copy(fig5_path, os.path.join(ARTIFACT_DIR, "fig5_year_blocked_errors.png"))
    
    # -------------------------------------------------------------
    # Figure 6: Prediction Interval Calibration Plots
    # -------------------------------------------------------------
    print("Generating Figure 6: Prediction Interval Calibration Plots...")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    
    # Top left: Bayesian Ridge 95% intervals over time for Hp-I
    ax_br = axes[0, 0]
    sub_br = oof_df[(oof_df["Model_Name"] == "M2_Bayesian_Ridge") & (oof_df["Basin_ID"] == "Hp-I")].sort_values("Validation_Year")
    yrs = sub_br["Validation_Year"].values
    ax_br.plot(yrs, sub_br["y_true"].values, "k-o", label="Observed", zorder=5)
    ax_br.plot(yrs, sub_br["y_pred"].values, color=MODEL_COLORS["M2_Bayesian_Ridge"], label="M2 Bayesian Ridge Pred")
    ax_br.fill_between(yrs, sub_br["y_pred"].values - 1.96 * sub_br["y_std"].values,
                       sub_br["y_pred"].values + 1.96 * sub_br["y_std"].values,
                       color=MODEL_COLORS["M2_Bayesian_Ridge"], alpha=0.25, label="Analytical 95% Credible Interval")
    ax_br.set_title("M2 Bayesian Ridge (Hp-I): Well-Calibrated (90% Coverage)")
    ax_br.set_ylabel("Volume Change (km³/yr)")
    ax_br.grid(True)
    ax_br.legend(loc="lower left", fontsize=8)
    
    # Top right: GPR 95% intervals over time for Hp-I
    ax_gp = axes[0, 1]
    sub_gp = oof_df[(oof_df["Model_Name"] == "M6_Gaussian_Process") & (oof_df["Basin_ID"] == "Hp-I")].sort_values("Validation_Year")
    ax_gp.plot(yrs, sub_gp["y_true"].values, "k-o", label="Observed", zorder=5)
    ax_gp.plot(yrs, sub_gp["y_pred"].values, color=MODEL_COLORS["M6_Gaussian_Process"], label="M6 GPR Pred")
    ax_gp.fill_between(yrs, sub_gp["y_pred"].values - 1.96 * sub_gp["y_std"].values,
                       sub_gp["y_pred"].values + 1.96 * sub_gp["y_std"].values,
                       color=MODEL_COLORS["M6_Gaussian_Process"], alpha=0.25, label="GPR 95% Interval (Overconfident)")
    ax_gp.set_title("M6 GPR (Hp-I): Severely Miscalibrated (10% Coverage)")
    ax_gp.set_ylabel("Volume Change (km³/yr)")
    ax_gp.grid(True)
    ax_gp.legend(loc="lower left", fontsize=8)
    
    # Bottom left: Bayesian Ridge Weighted (I-Ipp)
    ax_brw = axes[1, 0]
    sub_brw = oof_df[(oof_df["Model_Name"] == "M2_Bayesian_Ridge_Weighted") & (oof_df["Basin_ID"] == "I-Ipp")].sort_values("Validation_Year")
    ax_brw.plot(yrs, sub_brw["y_true"].values, "k-o", label="Observed", zorder=5)
    ax_brw.plot(yrs, sub_brw["y_pred"].values, color=MODEL_COLORS["M2_Bayesian_Ridge_Weighted"], label="M2 Weighted Pred")
    ax_brw.fill_between(yrs, sub_brw["y_pred"].values - 1.96 * sub_brw["y_std"].values,
                        sub_brw["y_pred"].values + 1.96 * sub_brw["y_std"].values,
                        color=MODEL_COLORS["M2_Bayesian_Ridge_Weighted"], alpha=0.25, label="Weighted 95% Credible Interval")
    ax_brw.set_title("M2 Weighted (I-Ipp): 100% Coverage (CRPS=6.04 km³/yr)")
    ax_brw.set_xlabel("Validation Year")
    ax_brw.set_ylabel("Volume Change (km³/yr)")
    ax_brw.grid(True)
    ax_brw.legend(loc="lower left", fontsize=8)
    
    # Bottom right: Bar chart of empirical coverage vs 95% target
    ax_cov = axes[1, 1]
    cov_sub = pi_df[pi_df["Basin_Scope"] == "POOLED_ALL_BASINS"]
    models_cov = cov_sub["Model_Name"].tolist()
    coverages = cov_sub["Empirical_Coverage_95pct"].tolist()
    bars = ax_cov.bar(range(len(models_cov)), coverages, color=[MODEL_COLORS.get(m, "gray") for m in models_cov], width=0.55)
    ax_cov.axhline(95, color="red", linestyle="--", linewidth=1.5, label="Target 95% Coverage")
    ax_cov.set_xticks(range(len(models_cov)))
    ax_cov.set_xticklabels([m.replace("_", "\n") for m in models_cov], fontsize=8)
    ax_cov.set_ylabel("Empirical 95% Coverage (%)")
    ax_cov.set_ylim(0, 110)
    ax_cov.set_title("Pooled Predictive Interval Coverage Comparison")
    ax_cov.grid(True, axis="y")
    ax_cov.legend(loc="lower right", fontsize=8)
    
    for bar, cov in zip(bars, coverages):
        ax_cov.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f"{cov:.1f}%",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
                    
    fig.suptitle("Probabilistic Uncertainty Calibration: Analytical Bayesian Likelihood vs. Kernel MLE", fontsize=14, y=0.98)
    plt.tight_layout()
    fig6_path = os.path.join(FIGURES_DIR, "fig6_prediction_interval_calibration.png")
    fig.savefig(fig6_path, dpi=300)
    plt.close(fig)
    shutil.copy(fig6_path, os.path.join(ARTIFACT_DIR, "fig6_prediction_interval_calibration.png"))
    
    print("\nAll 6 Phase 4B diagnostic figures successfully generated and copied to artifact directory!")

if __name__ == "__main__":
    generate_all_figures()

