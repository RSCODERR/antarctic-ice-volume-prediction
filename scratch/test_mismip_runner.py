import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np
import time

from src.physics.ssa_2d.constants import CONST_MISMIP
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d, compute_cfl_timestep_2d
from src.physics.ssa_2d.mismip_plus import (
    create_mismip_bed,
    compute_mismip_melt_rate,
    find_grounding_line_x,
)

print("Setting up MISMIP+ grid...")
# Domain: Lx = 640 km, Ly = 80 km
Lx = 640_000.0
Ly = 80_000.0
Nx = 64   # dx = 10 km
Ny = 9    # dy = 8.89 km

grid = Grid2D(Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip")
bed = create_mismip_bed(grid)

print(f"Bed stats: min={np.min(bed):.1f} m, max={np.max(bed):.1f} m, centerline divide={bed[grid.Ny//2, 0]:.1f} m")

# Initialize steady-like ice thickness:
# Near divide (x=0), H ~ 1500m. At x = 450 km, H ~ 600m. Towards calving front, floating shelf thinning to 300m.
x_c = grid.X
H = np.maximum(100.0, 1600.0 * (1.0 - 0.7 * (x_c / Lx)**0.7))

f_gr, s, H_flot = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)
x_gl = find_grounding_line_x(f_gr, grid)
print(f"Initial GL position: {x_gl / 1000.0:.2f} km")
print(f"Mean grounded fraction: {np.mean(f_gr):.3f}")

solver = SSASolver2D(const=CONST_MISMIP, omega=0.5, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5)
t0 = time.time()
res = solver.solve(grid, H, bed, s=s, raise_on_failure=False)
t_solve = time.time() - t0
print(f"Initial solve: converged={res.converged}, n_iter={res.n_iter}, time={t_solve:.2f} s")
print(f"Max velocity: {np.max(res.u)*CONST_MISMIP.sec_per_year:.1f} m/a, Front GL: {x_gl/1000.0:.1f} km")
