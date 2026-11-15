"""
scratch/test_resolution_convergence.py
=======================================
Controlled grid resolution comparison for MISMIP+:
  - Resolution 1: dx = 10.0 km, dy = 8.89 km (Nx=64, Ny=9)
  - Resolution 2: dx = 5.0 km,  dy = 5.0 km  (Nx=128, Ny=17)
  - Resolution 3: dx = 2.5 km,  dy = 2.5 km  (Nx=256, Ny=33)

Tests unforced steady-state grounding line position and Ice0 stability across resolutions.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.abspath("."))

import time
import numpy as np
import pandas as pd

from src.physics.ssa_2d.constants import CONST_MISMIP
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d
from src.physics.ssa_2d.mismip_plus import (
    create_mismip_bed,
    find_grounding_line_x,
    compute_vaf_km3,
    create_mismip_initial_profile,
)

print("=" * 78)
print("STAGE 4.2.3: CONTROLLED GRID-RESOLUTION COMPARISON (10 km, 5 km, 2.5 km)")
print("=" * 78)

resolutions = [
    {"name": "10 km", "dx_km": 10.0, "Nx": 64,  "Ny": 9,  "dt_yr": 1.0, "spinup_yrs": 80},
    {"name": "5 km",  "dx_km": 5.0,  "Nx": 128, "Ny": 17, "dt_yr": 0.5, "spinup_yrs": 60},
    {"name": "2.5 km","dx_km": 2.5,  "Nx": 256, "Ny": 33, "dt_yr": 0.25,"spinup_yrs": 40},
]

const = CONST_MISMIP
spy = const.sec_per_year
smb_si = 0.3 / spy

results = []

for cfg in resolutions:
    res_name = cfg["name"]
    Nx, Ny = cfg["Nx"], cfg["Ny"]
    dt_yr = cfg["dt_yr"]
    dt_sec = dt_yr * spy
    spinup_yrs = cfg["spinup_yrs"]
    n_steps = int(spinup_yrs / dt_yr)

    print(f"\n--- Testing Resolution: {res_name} (Nx={Nx}, Ny={Ny}, dx={640/Nx:.2f} km, dy={80/Ny:.2f} km) ---")
    grid = Grid2D(
        Lx=640_000.0, Ly=80_000.0, Nx=Nx, Ny=Ny,
        bc_west="no_slip", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
    )
    bed = create_mismip_bed(grid)
    solver = SSASolver2D(const=const, omega=0.6, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5 / spy)

    t0 = time.perf_counter()
    H = create_mismip_initial_profile(grid, bed, const, x_gl_target=450_000.0)
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s)
    u, v = res.u.copy(), res.v.copy()
    init_gl = find_grounding_line_x(f_gr, grid) / 1e3
    init_vaf = compute_vaf_km3(H, bed, grid, const)

    print(f"  Initialized profile: GL = {init_gl:.2f} km, VAF = {init_vaf:.1f} km3")
    print(f"  Initial solve: converged={res.converged}, iters={res.n_iter}, time={res.solve_time_sec:.3f} s")

    # Run spin-up
    prev_gl = init_gl
    for step in range(1, n_steps + 1):
        cur_yr = step * dt_yr
        rc = step_continuity_2d(H, u, v, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
        H = np.maximum(rc.H_next, 10.0)
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
        r = solver.solve(grid, H, bed, s=s, u_init=u, v_init=v, raise_on_failure=False)
        u, v = r.u, r.v

        if cur_yr % 20 == 0 or step == n_steps:
            cur_gl = find_grounding_line_x(f_gr, grid) / 1e3
            cur_vaf = compute_vaf_km3(H, bed, grid, const)
            dgl_dt = (cur_gl - prev_gl) / (20.0 if cur_yr > 20 else cur_yr)
            print(f"    Year {cur_yr:5.1f}: GL = {cur_gl:.2f} km, VAF = {cur_vaf:.1f} km3, rate = {dgl_dt:+.3f} km/yr, iters = {r.n_iter}")
            prev_gl = cur_gl

    wall_time = time.perf_counter() - t0
    final_gl = find_grounding_line_x(f_gr, grid) / 1e3
    final_vaf = compute_vaf_km3(H, bed, grid, const)

    results.append({
        "Resolution": res_name,
        "dx_km": 640.0 / Nx,
        "dy_km": 80.0 / Ny,
        "Total_Cells": Nx * Ny,
        "DOFs": 2 * Nx * Ny,
        "dt_yr": dt_yr,
        "Spinup_Yrs": spinup_yrs,
        "Initial_GL_km": init_gl,
        "Equilibrium_GL_km": final_gl,
        "Equilibrium_VAF_km3": final_vaf,
        "Wall_Time_Sec": wall_time,
    })

df_res = pd.DataFrame(results)
print("\n" + "=" * 78)
print("RESOLUTION CONVERGENCE SUMMARY:")
print(df_res.to_string(index=False))
df_res.to_csv("reports/tables/phase5_stage4_2_3_resolution_convergence.csv", index=False)

