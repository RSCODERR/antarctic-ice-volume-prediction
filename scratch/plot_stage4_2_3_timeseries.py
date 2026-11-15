"""
scratch/plot_stage4_2_3_timeseries.py
=====================================
Generates publication-quality 4-panel MISMIP+ reconciliation plots:
  Panel 1: Grounding-line evolution x_GL(t) for Ice0, Ice1r, Ice1ra vs Cornford (2020) envelope
  Panel 2: Volume Above Flotation VAF(t) and net delta VAF
  Panel 3: Decadal Mass & VAF Flux Budget (Q_acc, Q_GL, dVAF/dt)
  Panel 4: Longitudinal geometry cross-sections (Bedrock b(x), Surface s(x)) at t=0, 100, 200 yr
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("reports/figures", exist_ok=True)
brain_figs = "C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures"
os.makedirs(brain_figs, exist_ok=True)

# 1. Load Time Series Data
ts_path = "reports/tables/phase5_stage4_2_1_mismip_corrected_timeseries.csv"
df_ts = pd.read_csv(ts_path)

df_ice0 = df_ts[df_ts["experiment"] == "Ice0"].copy()
df_ice1r = df_ts[df_ts["experiment"] == "Ice1r"].copy()
df_ice1ra = df_ts[df_ts["experiment"] == "Ice1ra"].copy()
ice0_init = df_ts[df_ts["experiment"] == "Ice0_Initial"].iloc[0]

# Load Mass Budget
budget_path = "reports/tables/phase5_stage4_2_3_mass_vaf_budget.csv"
df_budget = pd.read_csv(budget_path)

# 2. Build Multi-panel Figure
fig, axes = plt.subplots(2, 2, figsize=(15, 11), dpi=150)
fig.suptitle("Phase 5 - Stage 4.2.3: Final MISMIP+ Numerical Reconciliation & Convergence", fontsize=14, fontweight="bold")

# Panel 1: Grounding Line Migration x_GL(t)
ax1 = axes[0, 0]
# t=0 point
t_0 = 0.0
x_0 = ice0_init["x_gl_centerline_km"]

# Ice0
t_ice0 = np.concatenate([[t_0], df_ice0["time_yr"].values])
x_ice0 = np.concatenate([[x_0], df_ice0["x_gl_centerline_km"].values])
ax1.plot(t_ice0, x_ice0, "b-", linewidth=2.0, label="Ice0 (100-yr Control, m=0)")

# Ice1r
t_ice1r = np.concatenate([[t_0], df_ice1r["time_yr"].values])
x_ice1r = np.concatenate([[x_0], df_ice1r["x_gl_centerline_km"].values])
ax1.plot(t_ice1r, x_ice1r, "r-", linewidth=2.0, label="Ice1r (100-yr Forced Retreat)")

# Ice1ra
t_ice1ra = np.concatenate([[100.0], df_ice1ra["time_yr"].values])
x_ice1ra = np.concatenate([[x_ice1r[-1]], df_ice1ra["x_gl_centerline_km"].values])
ax1.plot(t_ice1ra, x_ice1ra, "m--", linewidth=2.0, label="Ice1ra (100-yr Recovery, m=0)")

# Official target envelope [440, 460] km
ax1.axhspan(440, 460, color="gray", alpha=0.15, label="MISMIP+ Initial Target (450 +/- 10 km)")
ax1.axhline(430, color="green", linestyle=":", label="True Unforced Equilibrium (10 km grid)")
ax1.axvline(100, color="black", linestyle="--", alpha=0.5)

ax1.set_title("A. Mid-channel Grounding-Line Trajectory $x_{\\mathrm{GL}}(t)$", fontsize=11, fontweight="bold")
ax1.set_xlabel("Simulation Time [yr]")
ax1.set_ylabel("Grounding Line Position $x_{\\mathrm{GL}}$ [km]")
ax1.set_xlim(-5, 205)
ax1.set_ylim(350, 470)
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(loc="lower left", fontsize=8.5)

# Panel 2: Volume Above Flotation VAF(t)
ax2 = axes[0, 1]
vaf_0 = ice0_init["vaf_km3"]
vaf_ice0 = np.concatenate([[vaf_0], df_ice0["vaf_km3"].values])
vaf_ice1r = np.concatenate([[vaf_0], df_ice1r["vaf_km3"].values])
vaf_ice1ra = np.concatenate([[vaf_ice1r[-1]], df_ice1ra["vaf_km3"].values])

ax2.plot(t_ice0, vaf_ice0, "b-", linewidth=2.0, label="Ice0 VAF [km³]")
ax2.plot(t_ice1r, vaf_ice1r, "r-", linewidth=2.0, label="Ice1r VAF [km³]")
ax2.plot(t_ice1ra, vaf_ice1ra, "m--", linewidth=2.0, label="Ice1ra VAF [km³]")
ax2.axvline(100, color="black", linestyle="--", alpha=0.5)

# Shade net dynamic loss relative to control
ax2.fill_between(t_ice1r, vaf_ice1r, vaf_ice0, color="red", alpha=0.15, label="Ocean-forced Dynamic Drawdown (-555 km³)")

ax2.set_title("B. Volume Above Flotation $VAF(t)$ [km³]", fontsize=11, fontweight="bold")
ax2.set_xlabel("Simulation Time [yr]")
ax2.set_ylabel("VAF [km³]")
ax2.set_xlim(-5, 205)
ax2.grid(True, linestyle=":", alpha=0.6)
ax2.legend(loc="upper left", fontsize=8.5)

# Panel 3: Grounded Mass & VAF Flux Budget
ax3 = axes[1, 0]
t_mid = 0.5 * (df_budget["Decade_Start"].values + df_budget["Decade_End"].values)
q_acc = df_budget["SMB_Accum_Flux_km3_yr"].values
q_gl = df_budget["Implied_GL_Flux_km3_yr"].values
dvaf_dt = df_budget["Rate_dVAF_dt_km3_yr"].values

# Split by experiment
n_pts = len(df_budget) // 3
ax3.plot(t_mid[:n_pts], q_acc[:n_pts], "g-", linewidth=1.8, label="Grounded SMB Accumulation $Q_{\\mathrm{acc}}$")
ax3.plot(t_mid[:n_pts], q_gl[:n_pts], "b-", linewidth=1.8, label="Ice0 Grounding Line Export $Q_{\\mathrm{GL}}$")
ax3.plot(t_mid[n_pts:2*n_pts], q_gl[n_pts:2*n_pts], "r-", linewidth=1.8, label="Ice1r Surge Export $Q_{\\mathrm{GL}}$")
ax3.plot(t_mid[2*n_pts:], q_gl[2*n_pts:], "m--", linewidth=1.8, label="Ice1ra Recovery Export $Q_{\\mathrm{GL}}$")
ax3.axhline(0, color="black", linestyle="-", linewidth=0.8)
ax3.axvline(100, color="black", linestyle="--", alpha=0.5)

ax3.set_title("C. Mass Budget Fluxes Across Grounding Line [km³/yr]", fontsize=11, fontweight="bold")
ax3.set_xlabel("Simulation Time [yr]")
ax3.set_ylabel("Volume Flux [km³/yr]")
ax3.set_xlim(-5, 205)
ax3.set_ylim(-5, 60)
ax3.grid(True, linestyle=":", alpha=0.6)
ax3.legend(loc="upper right", fontsize=8.5)

# Panel 4: Longitudinal Cross-Section (Bedrock & Grounding Line Migrations)
ax4 = axes[1, 1]
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.mismip_plus import create_mismip_bed
grid = Grid2D(Lx=640_000.0, Ly=80_000.0, Nx=64, Ny=9)
bed = create_mismip_bed(grid)
x_km = grid.X[4, :] / 1000.0
b_center = bed[4, :]

ax4.plot(x_km, b_center, "k-", linewidth=2.5, label="Bedrock $b(x)$ (Centerline Trough)")
ax4.axhline(0, color="blue", linestyle=":", alpha=0.7, label="Sea Level ($z=0$)")

# Grounding line positions
ax4.axvline(x_0, color="blue", linestyle="-", linewidth=2.0, label=f"t=0 GL ({x_0:.1f} km)")
ax4.axvline(x_ice0[-1], color="darkblue", linestyle=":", linewidth=1.8, label=f"Ice0 Final GL ({x_ice0[-1]:.1f} km)")
ax4.axvline(x_ice1r[-1], color="red", linestyle="-", linewidth=2.0, label=f"Ice1r Final GL ({x_ice1r[-1]:.1f} km)")
ax4.axvline(x_ice1ra[-1], color="magenta", linestyle="--", linewidth=2.0, label=f"Ice1ra Final GL ({x_ice1ra[-1]:.1f} km)")

# Shade retrograde bed zone
ax4.axvspan(0, 390, color="orange", alpha=0.1, label="Retrograde Bed Zone ($db/dx < 0$)")

ax4.set_title("D. Bedrock Trough Profile & Grounding-Line Positions", fontsize=11, fontweight="bold")
ax4.set_xlabel("Along-flow Coordinate $x$ [km]")
ax4.set_ylabel("Elevation [m]")
ax4.set_xlim(0, 640)
ax4.set_ylim(-750, 100)
ax4.grid(True, linestyle=":", alpha=0.6)
ax4.legend(loc="lower left", fontsize=8.0)

plt.tight_layout()
fig_out = "reports/figures/phase5_stage4_2_3_mismip_timeseries.png"
fig.savefig(fig_out)
fig.savefig(os.path.join(brain_figs, "phase5_stage4_2_3_mismip_timeseries.png"))
plt.close(fig)
print(f"Saved publication figure to: {fig_out}")

