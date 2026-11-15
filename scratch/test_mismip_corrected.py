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

# Construct initial profile targeting x_GL = 450 km
x_gl_target = 450_000.0
x = grid.X
y = grid.Y

# Centerline bed at 450 km is ~ -627 m -> H_flot ~ 702 m
H = np.zeros_like(x)
mask_grounded = x <= x_gl_target
# Upstream profile: 1650 m at divide down to 705 m at 450 km
H[mask_grounded] = 1650.0 - (1650.0 - 705.0) * (x[mask_grounded] / x_gl_target)**0.65

# Floating shelf: 705 m at GL down to 250 m at front
mask_shelf = x > x_gl_target
H[mask_shelf] = 705.0 - (705.0 - 250.0) * ((x[mask_shelf] - x_gl_target) / (grid.Lx - x_gl_target))**0.5

# Transverse adjustment: add lateral profile matching trough
# Near walls, bed is 500m higher, so flotation thickness is smaller
# s_grounded = b + H
f_gr, s, H_flot = compute_flotation_fraction_and_surface(H, bed, const)
x_gl = find_grounding_line_x(f_gr, grid)
print(f"Constructed profile: centerline x_GL = {x_gl / 1000.0:.2f} km")

solver = SSASolver2D(const=const, omega=0.5, max_iter=100, tol_rel_residual=1e-5, tol_vel_step=0.5)
t0 = time.time()
res = solver.solve(grid, H, bed, s=s, raise_on_failure=False)
t_solve = time.time() - t0

print(f"Solve result: converged={res.converged}, iters={res.n_iter}, time={t_solve:.2f} s")
print(f"Max velocity: {np.max(res.u) * spy:.1f} m/a, Min velocity: {np.min(res.u) * spy:.1f} m/a")
print(f"Centerline velocity at GL: {res.u[grid.Ny//2, int(x_gl_target/grid.dx)] * spy:.1f} m/a")
