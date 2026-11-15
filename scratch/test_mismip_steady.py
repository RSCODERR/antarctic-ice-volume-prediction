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
    find_grounding_line_x,
)

grid = Grid2D(Lx=640_000.0, Ly=80_000.0, Nx=64, Ny=9, bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip")
bed = create_mismip_bed(grid)

spy = CONST_MISMIP.sec_per_year
dt_sec = 2.0 * spy
smb_si = 0.3 / spy

# Initial thickness
x_c = grid.X
H = np.maximum(100.0, 1600.0 * (1.0 - 0.7 * (x_c / grid.Lx)**0.7))

solver = SSASolver2D(const=CONST_MISMIP, omega=0.5, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5)

u_prev = None
v_prev = None

print("Running relaxation to steady state (200 yr)...")
for step in range(100):
    t_yr = (step + 1) * 2.0
    f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)
    res_ssa = solver.solve(grid, H, bed, s=s, u_init=u_prev, v_init=v_prev, raise_on_failure=False)
    u_prev = res_ssa.u
    v_prev = res_ssa.v

    res_cont = step_continuity_2d(H, u_prev, v_prev, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=CONST_MISMIP)
    dH_max = np.max(np.abs(res_cont.H_next - H)) / 2.0 # m/yr
    H = res_cont.H_next

    if (step + 1) % 20 == 0 or step == 0:
        f_gr, _, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)
        x_gl = find_grounding_line_x(f_gr, grid)
        print(f"Year {t_yr:3.0f}: x_GL = {x_gl/1000.0:.2f} km, dH_max = {dH_max:.3f} m/yr, max(u) = {np.max(u_prev)*spy:.1f} m/a")

# Save steady state
np.savez_compressed("scratch/mismip_steady_state.npz", H=H, u=u_prev, v=v_prev)
print("Steady state saved to scratch/mismip_steady_state.npz")

