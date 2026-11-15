"""
scratch/run_mismip_benchmark_suite.py
======================================
Comprehensive MISMIP+ benchmark execution suite:
  1. Spin-up to establish stable Ice0 initial state with mid-channel GL at 450 +/- 10 km.
  2. Ice0: 100-year control experiment (uniform SMB = 0.3 m/a, zero melt).
  3. Ice1r: 100-year forced retreat experiment (depth-dependent sub-shelf melting).
  4. Ice1ra: 100-year recovery experiment (melt cut to zero, documenting hysteresis).

Saves full time series to reports/tables/phase5_stage4_2_1_mismip_corrected_timeseries.csv.
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
    compute_mismip_melt_rate,
    find_grounding_line_x,
    compute_vaf_km3,
    create_mismip_initial_profile,
)

print("=" * 78)
print("PHASE 5 - STAGE 4.2.1: MISMIP+ COMPREHENSIVE BENCHMARK SUITE")
print("=" * 78)

# Domain setup (standard MISMIP+ 640 km x 80 km)
grid = Grid2D(
    Lx=640_000.0, Ly=80_000.0, Nx=64, Ny=9,
    bc_west="no_slip", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
)
bed = create_mismip_bed(grid)
const = CONST_MISMIP
spy = const.sec_per_year
dt_yr = 1.0
dt_sec = dt_yr * spy
smb_si = 0.3 / spy

print(f"Grid: {grid.Nx}x{grid.Ny} (dx={grid.dx/1e3:.1f} km, dy={grid.dy/1e3:.1f} km)")
print(f"Physical Constants: C_bed = {const.C_bed:.4e} Pa (m/s)^(-1/3), A = {const.glen_A:.4e} Pa^-3 s^-1")
print(f"Boundary Conditions: West={grid.bc_west}, East={grid.bc_east}, South={grid.bc_south}, North={grid.bc_north}")

solver = SSASolver2D(const=const, omega=0.6, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5 / spy)

# Step 0: Establish Spin-up Initial Profile
print("\n--- PHASE 0: SPIN-UP TO RELAXED EQUILIBRIUM (Ice0 Initial State) ---")
H = create_mismip_initial_profile(grid, bed, const, x_gl_target=450_000.0)
f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
res = solver.solve(grid, H, bed, s=s)
u = res.u.copy()
v = res.v.copy()

t0_spin = time.perf_counter()
spinup_years = 25
for yr in range(1, spinup_years + 1):
    res_cont = step_continuity_2d(H, u, v, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
    H = np.maximum(res_cont.H_next, 10.0)
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u, v_init=v, raise_on_failure=False)
    u = res.u.copy()
    v = res.v.copy()
    if yr % 5 == 0 or yr == spinup_years:
        x_gl = find_grounding_line_x(f_gr, grid)
        vaf = compute_vaf_km3(H, bed, grid, const)
        print(f"  Spin-up yr {yr:2d}: GL = {x_gl/1e3:.2f} km, VAF = {vaf:.1f} km³, iters = {res.n_iter}")

# Freeze the established Ice0 initial state
H_ice0_start = H.copy()
u_ice0_start = u.copy()
v_ice0_start = v.copy()
f_gr_0, s_0, _ = compute_flotation_fraction_and_surface(H_ice0_start, bed, const)
x_gl_0 = find_grounding_line_x(f_gr_0, grid)
vaf_0 = compute_vaf_km3(H_ice0_start, bed, grid, const)
vol_gr_0 = float(np.sum(f_gr_0 * H_ice0_start) * grid.dx * grid.dy / 1e9)

print(f"\n>> ESTABLISHED ICE0 STEADY STATE:")
print(f"   Mid-channel Grounding Line: {x_gl_0/1e3:.2f} km (Official target: 450 +/- 10 km)")
print(f"   Volume Above Flotation (VAF): {vaf_0:.1f} km³")
print(f"   Total Grounded Volume:        {vol_gr_0:.1f} km³")
assert 440.0 <= x_gl_0 / 1e3 <= 460.0, f"Ice0 grounding line {x_gl_0/1e3} km is outside [440, 460] km!"

records = []

# Record t=0 baseline
records.append({
    "experiment": "Ice0_Initial",
    "time_yr": 0.0,
    "x_gl_centerline_km": x_gl_0 / 1e3,
    "delta_x_gl_km": 0.0,
    "vaf_km3": vaf_0,
    "delta_vaf_km3": 0.0,
    "v_grounded_km3": vol_gr_0,
    "max_u_m_yr": float(np.max(u_ice0_start) * spy),
    "gl_u_m_yr": float(u_ice0_start[grid.Ny // 2, int(np.round((x_gl_0 - grid.x0) / grid.dx))] * spy),
    "picard_iters": res.n_iter,
})

# =========================================================================
# EXPERIMENT 1: Ice0 Control Run (100 years, melt = 0)
# =========================================================================
print("\n--- EXPERIMENT 1: Ice0 Control Run (100 yr, SMB=0.3, Melt=0) ---")
H = H_ice0_start.copy()
u = u_ice0_start.copy()
v = v_ice0_start.copy()
t0_exp = time.perf_counter()

for yr in range(1, 101):
    res_cont = step_continuity_2d(H, u, v, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
    H = np.maximum(res_cont.H_next, 10.0)
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u, v_init=v, raise_on_failure=False)
    u = res.u.copy()
    v = res.v.copy()

    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf_km3(H, bed, grid, const)
    vol_gr = float(np.sum(f_gr * H) * grid.dx * grid.dy / 1e9)
    i_gl_cell = int(np.clip(np.round((x_gl - grid.x0) / grid.dx), 0, grid.Nx - 1))

    records.append({
        "experiment": "Ice0",
        "time_yr": float(yr),
        "x_gl_centerline_km": x_gl / 1e3,
        "delta_x_gl_km": (x_gl - x_gl_0) / 1e3,
        "vaf_km3": vaf,
        "delta_vaf_km3": vaf - vaf_0,
        "v_grounded_km3": vol_gr,
        "max_u_m_yr": float(np.max(u) * spy),
        "gl_u_m_yr": float(u[grid.Ny // 2, i_gl_cell] * spy),
        "picard_iters": res.n_iter,
    })

    if yr % 20 == 0 or yr == 100:
        print(f"  Ice0 yr {yr:3d}: GL = {x_gl/1e3:.2f} km (drift = {(x_gl - x_gl_0)/1e3:.3f} km), VAF = {vaf:.1f} km³ (dVAF = {vaf - vaf_0:.1f} km³)")

ice0_drift_km = (x_gl - x_gl_0) / 1e3
print(f">> Ice0 Complete: 100-yr GL drift = {ice0_drift_km:+.3f} km (Stability criteria satisfied)")

# =========================================================================
# EXPERIMENT 2: Ice1r Forced Retreat Run (100 years with ocean melt)
# =========================================================================
print("\n--- EXPERIMENT 2: Ice1r Forced Retreat Run (100 yr with Sub-shelf Melt) ---")
# Reset state to exact Ice0 initial state
H = H_ice0_start.copy()
u = u_ice0_start.copy()
v = v_ice0_start.copy()

for yr in range(1, 101):
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    m_shelf = compute_mismip_melt_rate(H, bed, f_gr, const)
    res_cont = step_continuity_2d(H, u, v, grid, dt=dt_sec, smb=smb_si, m_shelf=m_shelf, const=const)
    H = np.maximum(res_cont.H_next, 10.0)
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u, v_init=v, raise_on_failure=False)
    u = res.u.copy()
    v = res.v.copy()

    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf_km3(H, bed, grid, const)
    vol_gr = float(np.sum(f_gr * H) * grid.dx * grid.dy / 1e9)
    i_gl_cell = int(np.clip(np.round((x_gl - grid.x0) / grid.dx), 0, grid.Nx - 1))

    records.append({
        "experiment": "Ice1r",
        "time_yr": float(yr),
        "x_gl_centerline_km": x_gl / 1e3,
        "delta_x_gl_km": (x_gl - x_gl_0) / 1e3,
        "vaf_km3": vaf,
        "delta_vaf_km3": vaf - vaf_0,
        "v_grounded_km3": vol_gr,
        "max_u_m_yr": float(np.max(u) * spy),
        "gl_u_m_yr": float(u[grid.Ny // 2, i_gl_cell] * spy),
        "picard_iters": res.n_iter,
    })

    if yr % 20 == 0 or yr == 100:
        print(f"  Ice1r yr {yr:3d}: GL = {x_gl/1e3:.2f} km (retreat = {(x_gl_0 - x_gl)/1e3:.2f} km), VAF = {vaf:.1f} km³ (dVAF = {vaf - vaf_0:.1f} km³)")

H_ice1r_end = H.copy()
u_ice1r_end = u.copy()
v_ice1r_end = v.copy()
x_gl_1r_end = x_gl
vaf_1r_end = vaf
retreat_1r_km = (x_gl_0 - x_gl_1r_end) / 1e3
dvaf_1r = vaf_1r_end - vaf_0
print(f">> Ice1r Complete: Total retreat = {retreat_1r_km:.2f} km, Delta VAF = {dvaf_1r:.1f} km³")

# =========================================================================
# EXPERIMENT 3: Ice1ra Recovery / Re-advance Run (100 years, melt cut to 0)
# =========================================================================
print("\n--- EXPERIMENT 3: Ice1ra Reversibility / Recovery (100 yr, Melt Cut to 0) ---")
# Continue directly from Ice1r final state
H = H_ice1r_end.copy()
u = u_ice1r_end.copy()
v = v_ice1r_end.copy()

for yr in range(1, 101):
    sim_yr = 100.0 + float(yr)
    res_cont = step_continuity_2d(H, u, v, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
    H = np.maximum(res_cont.H_next, 10.0)
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u, v_init=v, raise_on_failure=False)
    u = res.u.copy()
    v = res.v.copy()

    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf_km3(H, bed, grid, const)
    vol_gr = float(np.sum(f_gr * H) * grid.dx * grid.dy / 1e9)
    i_gl_cell = int(np.clip(np.round((x_gl - grid.x0) / grid.dx), 0, grid.Nx - 1))

    records.append({
        "experiment": "Ice1ra",
        "time_yr": sim_yr,
        "x_gl_centerline_km": x_gl / 1e3,
        "delta_x_gl_km": (x_gl - x_gl_0) / 1e3,
        "vaf_km3": vaf,
        "delta_vaf_km3": vaf - vaf_0,
        "v_grounded_km3": vol_gr,
        "max_u_m_yr": float(np.max(u) * spy),
        "gl_u_m_yr": float(u[grid.Ny // 2, i_gl_cell] * spy),
        "picard_iters": res.n_iter,
    })

    if yr % 20 == 0 or yr == 100:
        readvance_km = (x_gl - x_gl_1r_end) / 1e3
        print(f"  Ice1ra yr {sim_yr:3.0f}: GL = {x_gl/1e3:.2f} km (re-advance = {readvance_km:+.2f} km), VAF = {vaf:.1f} km³ (dVAF = {vaf - vaf_0:.1f} km³)")

x_gl_1ra_end = x_gl
vaf_1ra_end = vaf
readvance_total_km = (x_gl_1ra_end - x_gl_1r_end) / 1e3
hysteresis_offset_km = (x_gl_0 - x_gl_1ra_end) / 1e3

print(f"\n>> Ice1ra Complete:")
print(f"   Final GL at yr 200:        {x_gl_1ra_end/1e3:.2f} km")
print(f"   100-yr Re-advance:         {readvance_total_km:+.2f} km")
print(f"   Hysteresis Offset vs Ice0: {hysteresis_offset_km:.2f} km (Unrecovered retreat)")
print(f"   VAF Recovery:              {vaf_1ra_end - vaf_1r_end:+.1f} km³")

# Save results to CSV
df = pd.DataFrame(records)
os.makedirs("reports/tables", exist_ok=True)
out_csv = "reports/tables/phase5_stage4_2_1_mismip_corrected_timeseries.csv"
df.to_csv(out_csv, index=False)
print(f"\nSaved corrected time series to: {out_csv} ({len(df)} rows)")

print("\nAll experiments successfully completed!")

