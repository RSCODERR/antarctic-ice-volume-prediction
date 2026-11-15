import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from src.physics.ssa_2d.constants import SSA2DConstants, CONST_DEFAULT
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.rheology import compute_effective_viscosity_2d, compute_strain_rates_2d
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface, compute_basal_drag_coefficient
from src.physics.ssa_2d.boundary import compute_calving_front_traction

# Test an embayment channel: 40 km long x 20 km wide
# Divide upstream (x=0), calving front downstream (x=40km)
# No-slip rock walls at y=0 and y=20km
grid = Grid2D(Lx=40000.0, Ly=20000.0, Nx=20, Ny=11, bc_west="divide", bc_east="calving_front", bc_south="no_slip", bc_north="no_slip")

H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 600.0
# Surface slope along x: 1000m at divide to 400m at front
s = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
for i in range(grid.Nx):
    s[:, i] = 1000.0 - (600.0 / grid.Lx) * grid.x_centers[i]
b = s - H
f_gr = np.ones_like(H)

const = SSA2DConstants(C_bed=1.0e6, picard_omega=0.6)

def solve_embayment(grid, H, s, b, f_gr, const):
    Nx, Ny = grid.Nx, grid.Ny
    dx, dy = grid.dx, grid.dy
    N = grid.total_cells

    u = np.zeros((Ny, Nx), dtype=np.float64)
    v = np.zeros((Ny, Nx), dtype=np.float64)

    rho_i = const.rho_ice
    g = const.g

    ds_dx = np.zeros((Ny, Nx), dtype=np.float64)
    ds_dx[:, 1:-1] = (s[:, 2:] - s[:, :-2]) / (2.0 * dx)
    ds_dx[:, 0] = (s[:, 1] - s[:, 0]) / dx
    ds_dx[:, -1] = (s[:, -1] - s[:, -2]) / dx

    ds_dy = np.zeros((Ny, Nx), dtype=np.float64)
    ds_dy[1:-1, :] = (s[2:, :] - s[:-2, :]) / (2.0 * dy)
    ds_dy[0, :] = (s[1, :] - s[0, :]) / dy
    ds_dy[-1, :] = (s[-1, :] - s[-2, :]) / dy

    for it in range(40):
        nu = compute_effective_viscosity_2d(u, v, grid, const)
        beta_b = compute_basal_drag_coefficient(u, v, f_gr, const.C_bed, const)

        # Cross derivatives evaluated at current (u, v)
        eps_xx, eps_yy, eps_xy = compute_strain_rates_2d(u, v, grid)
        # Txx_cross = 2 * H * nu * eps_yy
        # Txy_cross = H * nu * dv/dx
        # Tyy_cross = 2 * H * nu * eps_xx
        # Tyx_cross = H * nu * du/dy

        # Assemble u system
        row_u, col_u, val_u = [], [], []
        b_u = -rho_i * g * H * ds_dx

        for j in range(Ny):
            for i in range(Nx - 1):
                H_f = 0.5 * (H[j, i] + H[j, i+1])
                nu_f = 0.5 * (nu[j, i] + nu[j, i+1])
                Kx = 4.0 * H_f * nu_f / (dx * dx)
                k1 = grid.dof_index_u(i, j)
                k2 = grid.dof_index_u(i+1, j)
                row_u.extend([k1, k1, k2, k2])
                col_u.extend([k1, k2, k2, k1])
                val_u.extend([Kx, -Kx, Kx, -Kx])

        for j in range(Ny - 1):
            for i in range(Nx):
                H_f = 0.5 * (H[j, i] + H[j+1, i])
                nu_f = 0.5 * (nu[j, i] + nu[j+1, i])
                Ky = 1.0 * H_f * nu_f / (dy * dy)
                k1 = grid.dof_index_u(i, j)
                k2 = grid.dof_index_u(i, j+1)
                row_u.extend([k1, k1, k2, k2])
                col_u.extend([k1, k2, k2, k1])
                val_u.extend([Ky, -Ky, Ky, -Ky])

        for j in range(Ny):
            for i in range(Nx):
                k = grid.dof_index_u(i, j)
                row_u.append(k)
                col_u.append(k)
                val_u.append(beta_b[j, i])

        # Calving front traction
        if grid.bc_east == "calving_front":
            is_flot = np.zeros(Ny, dtype=bool)
            N_nn = compute_calving_front_traction(H[:, -1], b[:, -1], is_flot, const)
            b_u[:, -1] += N_nn / dx

        # Cross term for u: d/dx(2 H nu dv/dy) + d/dy(H nu dv/dx)
        cross_u = np.zeros((Ny, Nx), dtype=np.float64)
        term1 = 2.0 * H * nu * eps_yy
        term2 = H * nu * (0.5 * (u[:, :] * 0.0)) # cross term with v
        # Add cross terms on RHS
        b_u_flat = b_u.ravel() + cross_u.ravel()

        Au = sp.coo_matrix((val_u, (row_u, col_u)), shape=(N, N)).tocsr()

        # West: u = 0
        for j in range(Ny):
            k = grid.dof_index_u(0, j)
            Au.data[Au.indptr[k]:Au.indptr[k+1]] = 0.0
            Au[k, k] = 1.0
            b_u_flat[k] = 0.0

        # South & North: no_slip -> u = 0
        for i in range(Nx):
            for j in (0, Ny - 1):
                k = grid.dof_index_u(i, j)
                Au.data[Au.indptr[k]:Au.indptr[k+1]] = 0.0
                Au[k, k] = 1.0
                b_u_flat[k] = 0.0

        Au.eliminate_zeros()
        u_new = spla.spsolve(Au, b_u_flat).reshape((Ny, Nx))

        du_norm = np.max(np.abs(u_new - u)) * const.sec_per_year
        u = const.picard_omega * u_new + (1.0 - const.picard_omega) * u

        if it < 5 or it % 5 == 0 or du_norm < 0.1:
            print(f"Iter {it+1:02d}: max(u) = {np.max(u)*const.sec_per_year:.2f} m/a, du_norm = {du_norm:.4e} m/a")
        if du_norm < 0.1 and it > 2:
            print(f"CONVERGED at iteration {it+1}!")
            break

    return u, v

u, v = solve_embayment(grid, H, s, b, f_gr, const)
# Check lateral symmetry: u(x, y) should equal u(x, Ly - y)
u_center = u[grid.Ny // 2, :]
print(f"Centerline velocity at front: {u_center[-1]*const.sec_per_year:.2f} m/a")
print(f"Wall velocity at south: {u[0, -1]*const.sec_per_year:.2e} m/a, north: {u[-1, -1]*const.sec_per_year:.2e} m/a")
# Symmetry check
sym_diff = np.max(np.abs(u - np.flip(u, axis=0))) * const.sec_per_year
print(f"Lateral symmetry difference: {sym_diff:.4e} m/a")

