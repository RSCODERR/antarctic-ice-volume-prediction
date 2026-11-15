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

def assemble_matrix(grid, H, s, b, nu, beta_b, const):
    Nx, Ny = grid.Nx, grid.Ny
    dx, dy = grid.dx, grid.dy
    N = grid.total_cells

    # Arrays for COO sparse matrix
    row_list = []
    col_list = []
    val_list = []
    
    bu = np.zeros((Ny, Nx), dtype=np.float64)
    bv = np.zeros((Ny, Nx), dtype=np.float64)

    # 1. Driving stress on cell centers
    # ds/dx
    ds_dx = np.zeros((Ny, Nx), dtype=np.float64)
    ds_dx[:, 1:-1] = (s[:, 2:] - s[:, :-2]) / (2.0 * dx)
    ds_dx[:, 0] = (s[:, 1] - s[:, 0]) / dx
    ds_dx[:, -1] = (s[:, -1] - s[:, -2]) / dx

    # ds/dy
    ds_dy = np.zeros((Ny, Nx), dtype=np.float64)
    ds_dy[1:-1, :] = (s[2:, :] - s[:-2, :]) / (2.0 * dy)
    ds_dy[0, :] = (s[1, :] - s[0, :]) / dy
    ds_dy[-1, :] = (s[-1, :] - s[-2, :]) / dy

    rho_i = const.rho_ice
    g = const.g
    bu = -rho_i * g * H * ds_dx
    bv = -rho_i * g * H * ds_dy

    # 2. Diffusion fluxes for u and v
    # x-faces: between (i, j) and (i+1, j) for i = 0 .. Nx-2
    for j in range(Ny):
        for i in range(Nx - 1):
            H_face = 0.5 * (H[j, i] + H[j, i + 1])
            nu_face = 0.5 * (nu[j, i] + nu[j, i + 1])
            Kx = 4.0 * H_face * nu_face / (dx * dx)
            Mx = 1.0 * H_face * nu_face / (dx * dx)

            ku1 = grid.dof_index_u(i, j)
            ku2 = grid.dof_index_u(i + 1, j)
            # u diffusion across x-face
            row_list.extend([ku1, ku1, ku2, ku2])
            col_list.extend([ku1, ku2, ku2, ku1])
            val_list.extend([Kx, -Kx, Kx, -Kx])

            kv1 = grid.dof_index_v(i, j)
            kv2 = grid.dof_index_v(i + 1, j)
            # v diffusion across x-face
            row_list.extend([kv1, kv1, kv2, kv2])
            col_list.extend([kv1, kv2, kv2, kv1])
            val_list.extend([Mx, -Mx, Mx, -Mx])

    # y-faces: between (i, j) and (i, j+1) for j = 0 .. Ny-2
    for j in range(Ny - 1):
        for i in range(Nx):
            H_face = 0.5 * (H[j, i] + H[j + 1, i])
            nu_face = 0.5 * (nu[j, i] + nu[j + 1, i])
            Ky = 1.0 * H_face * nu_face / (dy * dy)
            My = 4.0 * H_face * nu_face / (dy * dy)

            ku1 = grid.dof_index_u(i, j)
            ku2 = grid.dof_index_u(i, j + 1)
            # u diffusion across y-face
            row_list.extend([ku1, ku1, ku2, ku2])
            col_list.extend([ku1, ku2, ku2, ku1])
            val_list.extend([Ky, -Ky, Ky, -Ky])

            kv1 = grid.dof_index_v(i, j)
            kv2 = grid.dof_index_v(i, j + 1)
            # v diffusion across y-face
            row_list.extend([kv1, kv1, kv2, kv2])
            col_list.extend([kv1, kv2, kv2, kv1])
            val_list.extend([My, -My, My, -My])

    # 3. Basal drag on diagonal
    for j in range(Ny):
        for i in range(Nx):
            ku = grid.dof_index_u(i, j)
            kv = grid.dof_index_v(i, j)
            row_list.extend([ku, kv])
            col_list.extend([ku, kv])
            val_list.extend([beta_b[j, i], beta_b[j, i]])

    # 4. Calving front natural Neumann condition at x = x0 + Lx (i = Nx - 1)
    if grid.bc_east == "calving_front":
        is_flot = (b[:, -1] < 0) & (H[:, -1] <= -(const.rho_water / const.rho_ice) * b[:, -1])
        N_nn = compute_calving_front_traction(H[:, -1], b[:, -1], is_flot, const)
        bu[:, -1] += N_nn / dx

    # 5. Boundary conditions
    # Flatten RHS
    rhs = np.concatenate([bu.ravel(), bv.ravel()])

    # Dirichlet handling:
    # West: divide -> u = 0
    if grid.bc_west in ("divide", "free_slip"):
        for j in range(Ny):
            ku = grid.dof_index_u(0, j)
            # Find and clear entries in this row
            # A cleaner approach is to build matrix first, then zero rows
            pass

    A = sp.coo_matrix((val_list, (row_list, col_list)), shape=(2 * N, 2 * N)).tocsr()

    # Apply Dirichlet BCs by zeroing rows and setting diagonal = 1
    # West: divide -> u = 0
    if grid.bc_west in ("divide", "free_slip"):
        for j in range(Ny):
            ku = grid.dof_index_u(0, j)
            A.data[A.indptr[ku]:A.indptr[ku+1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0

    # South: free_slip -> v = 0
    if grid.bc_south in ("free_slip", "symmetry"):
        for i in range(Nx):
            kv = grid.dof_index_v(i, 0)
            A.data[A.indptr[kv]:A.indptr[kv+1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0
    elif grid.bc_south == "no_slip":
        for i in range(Nx):
            ku = grid.dof_index_u(i, 0)
            kv = grid.dof_index_v(i, 0)
            A.data[A.indptr[ku]:A.indptr[ku+1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0
            A.data[A.indptr[kv]:A.indptr[kv+1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0

    # North: free_slip -> v = 0
    if grid.bc_north in ("free_slip", "symmetry"):
        for i in range(Nx):
            kv = grid.dof_index_v(i, Ny - 1)
            A.data[A.indptr[kv]:A.indptr[kv+1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0
    elif grid.bc_north == "no_slip":
        for i in range(Nx):
            ku = grid.dof_index_u(i, Ny - 1)
            kv = grid.dof_index_v(i, Ny - 1)
            A.data[A.indptr[ku]:A.indptr[ku+1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0
            A.data[A.indptr[kv]:A.indptr[kv+1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0

    A.eliminate_zeros()
    return A, rhs

print("Running assembly test...")
grid = Grid2D(Lx=50000.0, Ly=20000.0, Nx=20, Ny=10, bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip")
H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 600.0
b = np.linspace(100.0, -300.0, grid.Nx).reshape(1, -1).repeat(grid.Ny, axis=0)
f_gr, s, H_flot = compute_flotation_fraction_and_surface(H, b, CONST_DEFAULT)

u = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
v = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)

for it in range(15):
    nu = compute_effective_viscosity_2d(u, v, grid, CONST_DEFAULT)
    beta_b = compute_basal_drag_coefficient(u, v, f_gr, CONST_DEFAULT.C_bed, CONST_DEFAULT)
    A, rhs = assemble_matrix(grid, H, s, b, nu, beta_b, CONST_DEFAULT)
    sol = spla.spsolve(A, rhs)
    u_new = sol[:grid.total_cells].reshape((grid.Ny, grid.Nx))
    v_new = sol[grid.total_cells:].reshape((grid.Ny, grid.Nx))
    
    du_inf = np.max(np.abs(u_new - u)) * CONST_DEFAULT.sec_per_year
    res_l2 = np.linalg.norm(A @ sol - rhs) / (np.linalg.norm(rhs) + 1e-12)
    
    u = 0.6 * u_new + 0.4 * u
    v = 0.6 * v_new + 0.4 * v
    print(f"Iter {it+1:02d}: max(u) = {np.max(u)*CONST_DEFAULT.sec_per_year:.2f} m/a, du_inf = {du_inf:.4e} m/a, rel_res = {res_l2:.4e}")
    if du_inf < 0.1:
        print("CONVERGED!")
        break
