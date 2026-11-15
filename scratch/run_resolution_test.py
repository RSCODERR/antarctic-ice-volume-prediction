"""
scratch/run_resolution_test.py
==============================
Controlled grid-resolution test for MISMIP+ (10 km, 5 km, 2.5 km).
Outputs progress directly with flush=True to verify execution.
"""
from __future__ import annotations
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

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

print("Starting Resolution Test...", flush=True)

const = CONST_MISMIP
spy = const.sec_per_year
smb_si = 0.3 / spy

# Grid configurations:
# dx = 10 km (Nx=64, Ny=9)
# dx = 5 km (Nx=128, Ny=17)
# dx = 2.5 km (Nx=256, Ny=33)
configs = [
    {"name": "10 km", "Nx": 64,  "Ny": 9,  "dt_yr": 1.0, "steps": 30},
    {"name": "5 km",  "Nx": 128, "Ny": 17, "dt_yr": 0.5, "steps": 30},
    {"name": "2.5 km","Nx": 256, "Ny": 33, "dt_yr": 0.25,"steps": 20},
]

records = []

for cfg in configs:
    name = cfg["name"]
    Nx, Ny = cfg["Nx"], cfg["Ny"]
    dt_yr = cfg["dt_yr"]
    dt_sec = dt_yr * spy
    steps = cfg["steps"]
    total_yr = steps * dt_yr

    print(f"\n==============================", flush=True)
    print(f"Testing {name}: Nx={Nx}, Ny={Ny}, dx={640/Nx:.2f} km, dt={dt_yr} yr, total={total_yr} yr", flush=True)
    print(f"==============================", flush=True)

    grid = Grid2D(
        Lx=640_000.0, Ly=80_000.0, Nx=Nx, Ny=Ny,
        bc_west="no_slip", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
    )
    bed = create_mismip_bed(grid)
    solver = SSASolver2D(const=const, omega=0.6, max_iter=60, tol_rel_residual=1e-5, tol_vel_step=0.5 / spy)

    H = create_mismip_initial_profile(grid, bed, const, x_gl_target=450_000.0)
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, raise_on_failure=False)
    u, v = res.u.copy(), res.v.copy()

    init_gl = find_grounding_line_x(f_gr, grid) / 1e3
    init_vaf = compute_vaf_km3(H, bed, grid, const)
    print(f"  Initialized: GL={init_gl:.2f} km, VAF={init_vaf:.1f} km3", flush=True)

    t0 = time.perf_counter()
    for st in range(1, steps + 1):
        cur_yr = st * dt_yr
        rc = step_continuity_2d(H, u, v, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
        H = np.maximum(rc.H_next, 10.0)
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
        r = solver.solve(grid, H, bed, s=s, u_init=u, v_init=v, raise_on_failure=False)
        u, v = r.u, r.v

        if cur_yr % 5.0 == 0 or st == steps:
            cur_gl = find_grounding_line_x(f_gr, grid) / 1e3
            cur_vaf = compute_vaf_km3(H, bed, grid, const)
            print(f"    Year {cur_yr:5.2f}: GL={cur_gl:.2f} km, VAF={cur_vaf:.1f} km3, iters={r.n_iter}", flush=True)

    wall_time = time.perf_counter() - t0
    final_gl = find_grounding_line_x(f_gr, grid) / 1e3
    final_vaf = compute_vaf_km3(H, bed, grid, const)

    records.append({
        "Resolution": name,
        "dx_km": 640.0 / Nx,
        "dy_km": 80.0 / Ny,
        "Total_Cells": Nx * Ny,
        "DOFs": 2 * Nx * Ny,
        "dt_yr": dt_yr,
        "Simulated_Yrs": total_yr,
        "Initial_GL_km": init_gl,
        "Final_GL_km": final_gl,
        "GL_Drift_km": final_gl - init_gl,
        "Initial_VAF_km3": init_vaf,
        "Final_VAF_km3": final_vaf,
        "Delta_VAF_km3": final_vaf - init_vaf,
        "Wall_Time_Sec": wall_time,
    })

df = pd.DataFrame(records)
print("\n" + "=" * 78, flush=True)
print("FINAL CONVERGENCE RESULTS:", flush=True)
print(df.to_string(index=False), flush=True)

out_csv = "reports/tables/phase5_stage4_2_3_resolution_convergence.csv"
df.to_csv(out_csv, index=False)
print(f"\nSaved results to {out_csv}", flush=True)

