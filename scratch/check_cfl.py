import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np

from src.physics.ssa_2d.constants import SSA2DConstants
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d, compute_cfl_timestep_2d
from src.physics.ssa_2d.mismip_plus import create_mismip_bed

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

x_gl_target = 450_000.0
x = grid.X
H = np.zeros_like(x)
mask_grounded = x <= x_gl_target
H[mask_grounded] = 1650.0 - (1650.0 - 705.0) * (x[mask_grounded] / x_gl_target)**0.65
mask_shelf = x > x_gl_target
H[mask_shelf] = 705.0 - (705.0 - 250.0) * ((x[mask_shelf] - x_gl_target) / (grid.Lx - x_gl_target))**0.5

solver = SSASolver2D(const=const, omega=0.5, max_iter=100)
f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, const)
res = solver.solve(grid, H, bed, s=s)

dt_cfl = compute_cfl_timestep_2d(res.u, res.v, grid, cfl_factor=0.5)
print(f"Max u: {np.max(res.u)*spy:.1f} m/a, Min u: {np.min(res.u)*spy:.1f} m/a")
print(f"CFL dt: {dt_cfl / spy:.3f} years ({dt_cfl:.1f} seconds)")

# Try 1 step with dt = 0.5 year
dt_step = 0.5 * spy
res_cont = step_continuity_2d(H, res.u, res.v, grid, dt=dt_step, smb=0.3/spy, const=const)
print(f"After step 1: min(H) = {np.min(res_cont.H_next):.1f} m, max(H) = {np.max(res_cont.H_next):.1f} m, NaN? {np.any(np.isnan(res_cont.H_next))}")

