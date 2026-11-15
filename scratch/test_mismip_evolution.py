import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np
import time

from src.physics.ssa_2d.constants import SSA2DConstants
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d
from src.physics.ssa_2d.mismip_plus import (
    create_mismip_bed,
    compute_mismip_melt_rate,
    find_grounding_line_x,
)

spy = 31536000.0
const = SSA2DConstants(
    rho_ice=918.0,
    rho_water=1028.0,
    g=9.8,
    glen_n=3.0,
    glen_A=2.0e-17 / spy,
    eps_0=1.0e-10,
    weertman_m=1.0 / 3.0,
    C_bed=3.160e6,
    u_0=1.0e-4 / spy,
    picard_omega=0.5,
    picard_max_iter=100,
    tol_rel_residual=1e-5,
    tol_vel_step=0.5,
    sec_per_year=spy,
)

grid = Grid2D(Lx=640_000.0, Ly=80_000.0, Nx=64, Ny=9, bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip")
bed = create_mismip_bed(grid)

def compute_vaf(H, b, grid, const):
    rho_i = const.rho_ice
    rho_w = const.rho_water
    b_sub = np.minimum(0.0, b)
    H_af = np.maximum(0.0, H + (rho_w / rho_i) * b_sub)
    vaf_m3 = np.sum(H_af) * grid.dx * grid.dy
    return float(vaf_m3 / 1.0e9)

# Construct initial profile targeting x_GL = 450 km
x_gl_target = 450_000.0
x = grid.X
H_init = np.zeros_like(x)
mask_grounded = x <= x_gl_target
H_init[mask_grounded] = 1650.0 - (1650.0 - 705.0) * (x[mask_grounded] / x_gl_target)**0.65
mask_shelf = x > x_gl_target
H_init[mask_shelf] = 705.0 - (705.0 - 250.0) * ((x[mask_shelf] - x_gl_target) / (grid.Lx - x_gl_target))**0.5

solver = SSASolver2D(const=const, omega=0.5, max_iter=100, tol_rel_residual=1e-5, tol_vel_step=0.5)

# First: Relax Ice0 to a true stable steady state
print("=== SPIN-UP TO STEADY STATE (Ice0) ===")
H = H_init.copy()
f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
u_prev = None
v_prev = None

dt_yr = 2.0
dt_sec = dt_yr * spy
smb_si = 0.3 / spy

# Run 50 steps (100 years) of spin-up to relax the initial profile
for step in range(50):
    t_yr = (step + 1) * dt_yr
    res = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
    u_prev = res.u
    v_prev = res.v
    res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
    H = res_cont.H_next
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf(H, bed, grid, const)
    if (step + 1) % 10 == 0:
        print(f"Spin-up Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, VAF = {vaf:.1f} km³, iters = {res.n_iter}")

H_ice0 = H.copy()
u_ice0 = u_prev.copy()
v_ice0 = v_prev.copy()
x_gl_0 = find_grounding_line_x(f_gr, grid)
vaf_0 = compute_vaf(H_ice0, bed, grid, const)
print(f"ESTABLISHED Ice0 Steady State: x_GL = {x_gl_0/1000.0:.2f} km, VAF = {vaf_0:.1f} km³")

# Experiment 1: Ice0 (100 years control run starting from steady state)
print("\n=== EXPERIMENT 1: Ice0 Control (100 yr) ===")
x_gl_ice0_series = []
vaf_ice0_series = []
H = H_ice0.copy()
u_prev = u_ice0.copy()
v_prev = v_ice0.copy()

for step in range(50):
    t_yr = (step + 1) * dt_yr
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
    u_prev = res.u
    v_prev = res.v
    res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
    H = res_cont.H_next
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf(H, bed, grid, const)
    x_gl_ice0_series.append((t_yr, x_gl))
    vaf_ice0_series.append((t_yr, vaf))
    if (step + 1) % 10 == 0:
        print(f"Ice0 Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, VAF = {vaf:.1f} km³, drift = {(x_gl - x_gl_0)/1000.0:.3f} km")

print(f"Ice0 Final (Year 100): x_GL = {x_gl/1000.0:.2f} km, 100-yr drift = {(x_gl - x_gl_0)/1000.0:.3f} km")

# Experiment 2: Ice1r (100 years retreat under melt forcing starting from Ice0)
print("\n=== EXPERIMENT 2: Ice1r Forced Retreat (100 yr) ===")
x_gl_ice1r_series = []
vaf_ice1r_series = []
H = H_ice0.copy()
u_prev = u_ice0.copy()
v_prev = v_ice0.copy()

for step in range(50):
    t_yr = (step + 1) * dt_yr
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
    u_prev = res.u
    v_prev = res.v
    m_shelf = compute_mismip_melt_rate(H, bed, f_gr, const)
    res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=m_shelf, const=const)
    H = res_cont.H_next
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf(H, bed, grid, const)
    x_gl_ice1r_series.append((t_yr, x_gl))
    vaf_ice1r_series.append((t_yr, vaf))
    if (step + 1) % 10 == 0:
        print(f"Ice1r Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, VAF = {vaf:.1f} km³, retreat = {(x_gl_0 - x_gl)/1000.0:.2f} km")

H_ice1r_end = H.copy()
u_ice1r_end = u_prev.copy()
v_ice1r_end = v_prev.copy()
x_gl_1r_end = x_gl
vaf_1r_end = vaf
print(f"Ice1r Final (Year 100): x_GL = {x_gl_1r_end/1000.0:.2f} km, total retreat = {(x_gl_0 - x_gl_1r_end)/1000.0:.2f} km, Delta VAF = {vaf_1r_end - vaf_0:.1f} km³")

# Experiment 3: Ice1ra (100 years re-advance / relaxation starting from end of Ice1r)
print("\n=== EXPERIMENT 3: Ice1ra Recovery / Re-advance (100 yr) ===")
x_gl_ice1ra_series = []
vaf_ice1ra_series = []
H = H_ice1r_end.copy()
u_prev = u_ice1r_end.copy()
v_prev = v_ice1r_end.copy()

for step in range(50):
    t_yr = 100.0 + (step + 1) * dt_yr
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    res = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
    u_prev = res.u
    v_prev = res.v
    res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=const)
    H = res_cont.H_next
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
    x_gl = find_grounding_line_x(f_gr, grid)
    vaf = compute_vaf(H, bed, grid, const)
    x_gl_ice1ra_series.append((t_yr, x_gl))
    vaf_ice1ra_series.append((t_yr, vaf))
    if (step + 1) % 10 == 0:
        print(f"Ice1ra Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, VAF = {vaf:.1f} km³, re-advance = {(x_gl - x_gl_1r_end)/1000.0:.2f} km")

x_gl_1ra_end = x_gl
vaf_1ra_end = vaf
print(f"Ice1ra Final (Year 200): x_GL = {x_gl_1ra_end/1000.0:.2f} km, re-advance = {(x_gl_1ra_end - x_gl_1r_end)/1000.0:.2f} km, Delta VAF recovery = {vaf_1ra_end - vaf_1r_end:.1f} km³")

