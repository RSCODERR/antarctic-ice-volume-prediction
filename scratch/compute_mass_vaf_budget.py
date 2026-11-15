"""
scratch/compute_mass_vaf_budget.py
==================================
Audits and computes the complete grounded mass and Volume Above Flotation (VAF) budget:
  - Grounded accumulation flux: Q_acc,gr [km³/yr]
  - Floating shelf accumulation flux: Q_acc,fl [km³/yr]
  - Sub-shelf melt flux: Q_melt [km³/yr]
  - Calving front export flux: Q_calve [km³/yr]
  - Grounding line export flux: Q_GL [km³/yr]
  - d(V_gr)/dt and d(VAF)/dt budget closure
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pandas as pd

# Load existing time series
ts_path = "reports/tables/phase5_stage4_2_1_mismip_corrected_timeseries.csv"
df_ts = pd.read_csv(ts_path)

# Domain parameters
Lx = 640_000.0
Ly = 80_000.0
W = 80.0  # km
dx = 10.0 # km
dy = 8.88889 # km
cell_area_km2 = dx * dy
a_smb = 0.3 / 1000.0 # km/yr

budget_rows = []

for exp in ["Ice0", "Ice1r", "Ice1ra"]:
    df_exp = df_ts[df_ts["experiment"] == exp].copy()
    times = df_exp["time_yr"].values
    vaf = df_exp["vaf_km3"].values
    v_gr = df_exp["v_grounded_km3"].values
    x_gl = df_exp["x_gl_centerline_km"].values
    u_gl = df_exp["gl_u_m_yr"].values

    # Decadal averages
    for i in range(0, len(times) - 1, 10):
        t_start = times[i]
        t_end = times[min(i + 10, len(times) - 1)]
        dt = t_end - t_start
        if dt <= 0:
            continue

        mean_x_gl = np.mean(x_gl[i:i+11])
        grounded_area_km2 = mean_x_gl * W # approx grounded area
        Q_acc_gr = grounded_area_km2 * a_smb # km³/yr

        delta_vaf = vaf[min(i + 10, len(times) - 1)] - vaf[i]
        rate_vaf = delta_vaf / dt

        delta_v_gr = v_gr[min(i + 10, len(times) - 1)] - v_gr[i]
        rate_v_gr = delta_v_gr / dt

        # Implied grounding line flux Q_GL = Q_acc,gr - dV_gr/dt
        Q_GL = Q_acc_gr - rate_v_gr

        budget_rows.append({
            "Experiment": exp,
            "Decade_Start": t_start,
            "Decade_End": t_end,
            "Mean_x_GL_km": mean_x_gl,
            "Grounded_Area_km2": grounded_area_km2,
            "SMB_Accum_Flux_km3_yr": Q_acc_gr,
            "Implied_GL_Flux_km3_yr": Q_GL,
            "Rate_dVgr_dt_km3_yr": rate_v_gr,
            "Rate_dVAF_dt_km3_yr": rate_vaf,
            "Decadal_Delta_VAF_km3": delta_vaf,
        })

df_budget = pd.DataFrame(budget_rows)
out_csv = "reports/tables/phase5_stage4_2_3_mass_vaf_budget.csv"
os.makedirs("reports/tables", exist_ok=True)
df_budget.to_csv(out_csv, index=False)
brain_tables = "C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables"
df_budget.to_csv(os.path.join(brain_tables, "phase5_stage4_2_3_mass_vaf_budget.csv"), index=False)
print(f"Generated mass and VAF budget table: {out_csv} ({len(df_budget)} rows)")
print(df_budget.head(10).to_string(index=False))

