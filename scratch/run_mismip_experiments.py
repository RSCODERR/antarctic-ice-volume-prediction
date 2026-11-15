import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import time
import numpy as np

from src.physics.ssa_2d.constants import CONST_MISMIP
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d
from src.physics.ssa_2d.mismip_plus import (
    create_mismip_bed,
    compute_mismip_melt_rate,
    find_grounding_line_x,
    MISMIPResult,
)

def run_mismip_suite(dt_yr=5.0, n_steps=20):
    # Total duration = dt_yr * n_steps = 100 years per experiment
    Lx = 640_000.0
    Ly = 80_000.0
    Nx = 64
    Ny = 9

    grid = Grid2D(Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip")
    bed = create_mismip_bed(grid)

    spy = CONST_MISMIP.sec_per_year
    dt_sec = dt_yr * spy
    smb_si = 0.3 / spy  # 0.3 m/yr

    # Initial thickness
    x_c = grid.X
    H_init = np.maximum(100.0, 1600.0 * (1.0 - 0.7 * (x_c / Lx)**0.7))

    solver = SSASolver2D(const=CONST_MISMIP, omega=0.5, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5)

    print("=== EXPERIMENT 1: ice0 (Steady State / Control, 100 yr) ===")
    t0_exp = time.time()
    H = H_init.copy()
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)
    u_prev = None
    v_prev = None

    iters_ice0 = []
    x_gl_hist_ice0 = []
    vol_hist_ice0 = []

    for step in range(n_steps):
        t_yr = (step + 1) * dt_yr
        res_ssa = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
        iters_ice0.append(res_ssa.n_iter)
        u_prev = res_ssa.u
        v_prev = res_ssa.v

        # Update thickness (zero ocean melt in ice0)
        res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=CONST_MISMIP)
        H = res_cont.H_next
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)

        x_gl = find_grounding_line_x(f_gr, grid)
        # Grounded volume in km3: sum(f_gr * H * dx * dy) / 1e9
        v_gr = float(np.sum(f_gr * H) * grid.dx * grid.dy / 1.0e9)

        x_gl_hist_ice0.append(x_gl)
        vol_hist_ice0.append(v_gr)
        if (step + 1) % 5 == 0 or step == 0:
            print(f"ice0 Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, V_grounded = {v_gr:.1f} km³, max(u) = {np.max(u_prev)*spy:.1f} m/a (Picard iters: {res_ssa.n_iter})")

    runtime_ice0 = time.time() - t0_exp
    H_ice0_final = H.copy()
    u_ice0_final = u_prev.copy()
    v_ice0_final = v_prev.copy()

    print("\n=== EXPERIMENT 2: ice1r (Forced Retreat under Sub-Shelf Melt, 100 yr) ===")
    t0_exp = time.time()
    iters_ice1r = []
    x_gl_hist_ice1r = []
    vol_hist_ice1r = []

    for step in range(n_steps):
        t_yr = (step + 1) * dt_yr
        res_ssa = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
        iters_ice1r.append(res_ssa.n_iter)
        u_prev = res_ssa.u
        v_prev = res_ssa.v

        # Sub-shelf melt rate
        m_shelf_si = compute_mismip_melt_rate(H, bed, f_gr, CONST_MISMIP)

        # Update thickness
        res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=m_shelf_si, const=CONST_MISMIP)
        H = res_cont.H_next
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)

        x_gl = find_grounding_line_x(f_gr, grid)
        v_gr = float(np.sum(f_gr * H) * grid.dx * grid.dy / 1.0e9)

        x_gl_hist_ice1r.append(x_gl)
        vol_hist_ice1r.append(v_gr)
        if (step + 1) % 5 == 0 or step == 0:
            print(f"ice1r Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, V_grounded = {v_gr:.1f} km³, max(u) = {np.max(u_prev)*spy:.1f} m/a (Picard iters: {res_ssa.n_iter})")

    runtime_ice1r = time.time() - t0_exp
    H_ice1r_final = H.copy()

    print("\n=== EXPERIMENT 3: ice1ra (Re-advance & Reversibility Test, 100 yr) ===")
    t0_exp = time.time()
    iters_ice1ra = []
    x_gl_hist_ice1ra = []
    vol_hist_ice1ra = []

    for step in range(n_steps):
        t_yr = 100.0 + (step + 1) * dt_yr
        res_ssa = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
        iters_ice1ra.append(res_ssa.n_iter)
        u_prev = res_ssa.u
        v_prev = res_ssa.v

        # Ocean melt cut back to 0.0
        res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=CONST_MISMIP)
        H = res_cont.H_next
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)

        x_gl = find_grounding_line_x(f_gr, grid)
        v_gr = float(np.sum(f_gr * H) * grid.dx * grid.dy / 1.0e9)

        x_gl_hist_ice1ra.append(x_gl)
        vol_hist_ice1ra.append(v_gr)
        if (step + 1) % 5 == 0 or step == 0:
            print(f"ice1ra Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, V_grounded = {v_gr:.1f} km³, max(u) = {np.max(u_prev)*spy:.1f} m/a (Picard iters: {res_ssa.n_iter})")

    runtime_ice1ra = time.time() - t0_exp

    # Reversibility analysis: offset between unpinned baseline and recovered state
    hysteresis_offset_m = abs(x_gl_hist_ice1ra[-1] - x_gl_hist_ice0[-1])

    print("\n=== MISMIP+ SUITE SUMMARY ===")
    print(f"ice0 steady x_GL: {x_gl_hist_ice0[-1]/1000.0:.2f} km (Standard target: [450, 480] km)")
    print(f"ice1r minimum x_GL: {min(x_gl_hist_ice1r)/1000.0:.2f} km (Retreat distance: {(x_gl_hist_ice0[-1] - min(x_gl_hist_ice1r))/1000.0:.2f} km)")
    print(f"ice1ra recovered x_GL: {x_gl_hist_ice1ra[-1]/1000.0:.2f} km (Re-advance: {(x_gl_hist_ice1ra[-1] - min(x_gl_hist_ice1r))/1000.0:.2f} km)")
    print(f"Reversibility Hysteresis Offset: {hysteresis_offset_m:.2f} m (Acceptance limit: < {grid.dx:.1f} m)")
    print(f"Runtimes: ice0={runtime_ice0:.2f} s, ice1r={runtime_ice1r:.2f} s, ice1ra={runtime_ice1ra:.2f} s")

if __name__ == "__main__":
    run_mismip_suite()

