import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np
import scipy.sparse.linalg as spla

from src.physics.ssa_2d.constants import SSA2DConstants
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.rheology import compute_effective_viscosity_2d
from src.physics.ssa_2d.friction import compute_basal_drag_coefficient
from scratch.test_coupled_solver import assemble_coupled_ssa_system

grid = Grid2D(Lx=40000.0, Ly=20000.0, Nx=20, Ny=11, bc_west="divide", bc_east="calving_front", bc_south="no_slip", bc_north="no_slip")
H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 600.0
s = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
for i in range(grid.Nx):
    s[:, i] = 1000.0 - (100.0 / grid.Lx) * grid.x_centers[i]
b = s - H
f_gr = np.ones_like(H)

const = SSA2DConstants(C_bed=5.0e6, picard_omega=0.6)

# Initialise with driving stress estimate: tau_d = rho g H (100 / 40000) = 13.5 kPa
tau_d = const.rho_ice * const.g * 600.0 * (100.0 / 40000.0)
u_est = (tau_d / const.C_bed)**3.0 # ~ 2.0e-4 m/s ~ 6000 m/a

u = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * u_est
# Enforce boundary values on init
u[:, 0] = 0.0
u[0, :] = 0.0
u[-1, :] = 0.0
v = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)

print(f"Initial u estimate: {u_est * const.sec_per_year:.1f} m/a")
for it in range(30):
    nu = compute_effective_viscosity_2d(u, v, grid, const)
    beta_b = compute_basal_drag_coefficient(u, v, f_gr, const.C_bed, const)
    A, rhs = assemble_coupled_ssa_system(grid, H, s, b, nu, beta_b, const)
    sol = spla.spsolve(A, rhs)
    
    u_new = sol[:grid.total_cells].reshape((grid.Ny, grid.Nx))
    v_new = sol[grid.total_cells:].reshape((grid.Ny, grid.Nx))
    
    du_norm = np.max(np.abs(u_new - u)) * const.sec_per_year
    dv_norm = np.max(np.abs(v_new - v)) * const.sec_per_year
    max_d = max(du_norm, dv_norm)
    
    u = const.picard_omega * u_new + (1.0 - const.picard_omega) * u
    v = const.picard_omega * v_new + (1.0 - const.picard_omega) * v
    
    print(f"Iter {it+1:02d}: max(u) = {np.max(u)*const.sec_per_year:.2f} m/a, max_step = {max_d:.4e} m/a")
    if max_d < 0.1:
        print(f"CONVERGED at iteration {it+1}!")
        break
