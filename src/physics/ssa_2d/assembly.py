"""
src/physics/ssa_2d/assembly.py
==============================
Sparse matrix assembly for the 2D Shallow Shelf Approximation (SSA) momentum system.

Assembles the discrete non-linear Picard system:
  A(u^k, v^k) [u^(k+1), v^(k+1)]^T = b

Degrees of freedom:
  - Total cells: N = Nx * Ny
  - Total DOFs: 2 * N
  - u(i, j) index: j * Nx + i
  - v(i, j) index: N + j * Nx + i
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
import scipy.sparse as sp

from .constants import SSA2DConstants, CONST_DEFAULT
from .grid import Grid2D
from .boundary import compute_calving_front_traction


def assemble_ssa_system_2d(
    grid: Grid2D,
    H: NDArray[np.float64],
    s: NDArray[np.float64],
    b: NDArray[np.float64],
    nu: NDArray[np.float64],
    beta_b: NDArray[np.float64],
    const: SSA2DConstants = CONST_DEFAULT,
    u_dirichlet: NDArray[np.float64] | None = None,
    v_dirichlet: NDArray[np.float64] | None = None,
) -> tuple[sp.csr_matrix, NDArray[np.float64]]:
    """
    Assemble the coupled 2D SSA sparse linear system A w = rhs in SciPy CSR format.

    Parameters
    ----------
    grid : Grid2D
        2D structured Cartesian mesh.
    H : NDArray[np.float64]
        Ice thickness [m] (Ny, Nx).
    s : NDArray[np.float64]
        Ice surface elevation [m] (Ny, Nx).
    b : NDArray[np.float64]
        Bedrock elevation [m] (Ny, Nx).
    nu : NDArray[np.float64]
        Effective viscosity [Pa s] (Ny, Nx).
    beta_b : NDArray[np.float64]
        Basal drag coefficient [Pa s m⁻¹] (Ny, Nx).
    const : SSA2DConstants
    u_dirichlet : NDArray[np.float64] | None
        Optional prescribed Dirichlet values for u.
    v_dirichlet : NDArray[np.float64] | None
        Optional prescribed Dirichlet values for v.

    Returns
    -------
    A : sp.csr_matrix
        Sparse system matrix of shape (2*N, 2*N).
    rhs : NDArray[np.float64]
        Right-hand side vector of length 2*N.
    """
    Nx, Ny = grid.Nx, grid.Ny
    dx, dy = grid.dx, grid.dy
    N = grid.total_cells

    row_list: list[int] = []
    col_list: list[int] = []
    val_list: list[float] = []

    # 1. Driving stress: tau_d = - rho_i * g * H * grad(s)
    ds_dx = np.zeros((Ny, Nx), dtype=np.float64)
    ds_dx[:, 1:-1] = (s[:, 2:] - s[:, :-2]) / (2.0 * dx)
    ds_dx[:, 0] = (s[:, 1] - s[:, 0]) / dx
    ds_dx[:, -1] = (s[:, -1] - s[:, -2]) / dx

    ds_dy = np.zeros((Ny, Nx), dtype=np.float64)
    ds_dy[1:-1, :] = (s[2:, :] - s[:-2, :]) / (2.0 * dy)
    ds_dy[0, :] = (s[1, :] - s[0, :]) / dy
    ds_dy[-1, :] = (s[-1, :] - s[-2, :]) / dy

    rho_i = const.rho_ice
    g = const.g
    bu = -rho_i * g * H * ds_dx
    bv = -rho_i * g * H * ds_dy

    # 2. Main diffusion operators
    # x-faces: between (i, j) and (i+1, j) for i = 0 .. Nx-2
    for j in range(Ny):
        for i in range(Nx - 1):
            Hf = 0.5 * (H[j, i] + H[j, i + 1])
            nuf = 0.5 * (nu[j, i] + nu[j, i + 1])
            Kx = 4.0 * Hf * nuf / (dx * dx)
            Mx = 1.0 * Hf * nuf / (dx * dx)

            ku1 = grid.dof_index_u(i, j)
            ku2 = grid.dof_index_u(i + 1, j)
            row_list.extend([ku1, ku1, ku2, ku2])
            col_list.extend([ku1, ku2, ku2, ku1])
            val_list.extend([Kx, -Kx, Kx, -Kx])

            kv1 = grid.dof_index_v(i, j)
            kv2 = grid.dof_index_v(i + 1, j)
            row_list.extend([kv1, kv1, kv2, kv2])
            col_list.extend([kv1, kv2, kv2, kv1])
            val_list.extend([Mx, -Mx, Mx, -Mx])

    # y-faces: between (i, j) and (i, j+1) for j = 0 .. Ny-2
    for j in range(Ny - 1):
        for i in range(Nx):
            Hf = 0.5 * (H[j, i] + H[j + 1, i])
            nuf = 0.5 * (nu[j, i] + nu[j + 1, i])
            Ky = 1.0 * Hf * nuf / (dy * dy)
            My = 4.0 * Hf * nuf / (dy * dy)

            ku1 = grid.dof_index_u(i, j)
            ku2 = grid.dof_index_u(i, j + 1)
            row_list.extend([ku1, ku1, ku2, ku2])
            col_list.extend([ku1, ku2, ku2, ku1])
            val_list.extend([Ky, -Ky, Ky, -Ky])

            kv1 = grid.dof_index_v(i, j)
            kv2 = grid.dof_index_v(i, j + 1)
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
            val_list.extend([float(beta_b[j, i]), float(beta_b[j, i])])

    # 4. Cross-coupling terms (interior stencil)
    c_factor = 3.0 / (4.0 * dx * dy)
    for j in range(1, Ny - 1):
        for i in range(1, Nx - 1):
            Hnu = float(H[j, i] * nu[j, i] * c_factor)
            ku = grid.dof_index_u(i, j)
            kv = grid.dof_index_v(i, j)

            # u-equation coupling to v: - Hnu * (v_{i+1, j+1} - v_{i-1, j+1} - v_{i+1, j-1} + v_{i-1, j-1})
            kv_pp = grid.dof_index_v(i + 1, j + 1)
            kv_mp = grid.dof_index_v(i - 1, j + 1)
            kv_pm = grid.dof_index_v(i + 1, j - 1)
            kv_mm = grid.dof_index_v(i - 1, j - 1)

            row_list.extend([ku, ku, ku, ku])
            col_list.extend([kv_pp, kv_mp, kv_pm, kv_mm])
            val_list.extend([-Hnu, Hnu, Hnu, -Hnu])

            # v-equation coupling to u: - Hnu * (u_{i+1, j+1} - u_{i-1, j+1} - u_{i+1, j-1} + u_{i-1, j-1})
            ku_pp = grid.dof_index_u(i + 1, j + 1)
            ku_mp = grid.dof_index_u(i - 1, j + 1)
            ku_pm = grid.dof_index_u(i + 1, j - 1)
            ku_mm = grid.dof_index_u(i - 1, j - 1)

            row_list.extend([kv, kv, kv, kv])
            col_list.extend([ku_pp, ku_mp, ku_pm, ku_mm])
            val_list.extend([-Hnu, Hnu, Hnu, -Hnu])

    # 5. Calving front natural normal stress traction at x = x0 + Lx (i = Nx - 1)
    if grid.bc_east == "calving_front":
        is_flot = (b[:, -1] < 0) & (H[:, -1] <= -(const.rho_water / const.rho_ice) * b[:, -1])
        N_nn = compute_calving_front_traction(H[:, -1], b[:, -1], is_flot, const)
        bu[:, -1] += N_nn / dx

    rhs = np.concatenate([bu.ravel(), bv.ravel()])
    A = sp.coo_matrix((val_list, (row_list, col_list)), shape=(2 * N, 2 * N)).tocsr()

    # 6. Apply Boundary Conditions (Dirichlet and divide)
    # West: divide -> u = 0, zero shear for v
    if grid.bc_west in ("divide", "free_slip"):
        for j in range(Ny):
            ku = grid.dof_index_u(0, j)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0
    elif grid.bc_west == "no_slip":
        for j in range(Ny):
            ku = grid.dof_index_u(0, j)
            kv = grid.dof_index_v(0, j)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0
            A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0
    elif grid.bc_west == "dirichlet" and u_dirichlet is not None:
        for j in range(Ny):
            ku = grid.dof_index_u(0, j)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = float(u_dirichlet[j, 0])
            if v_dirichlet is not None:
                kv = grid.dof_index_v(0, j)
                A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
                A[kv, kv] = 1.0
                rhs[kv] = float(v_dirichlet[j, 0])

    # East: dirichlet
    if grid.bc_east == "dirichlet" and u_dirichlet is not None:
        for j in range(Ny):
            ku = grid.dof_index_u(Nx - 1, j)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = float(u_dirichlet[j, -1])
            if v_dirichlet is not None:
                kv = grid.dof_index_v(Nx - 1, j)
                A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
                A[kv, kv] = 1.0
                rhs[kv] = float(v_dirichlet[j, -1])
    elif grid.bc_east == "free_slip":
        for j in range(Ny):
            ku = grid.dof_index_u(Nx - 1, j)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0

    # South: free_slip (v=0) or no_slip (u=0, v=0)
    if grid.bc_south in ("free_slip", "symmetry"):
        for i in range(Nx):
            kv = grid.dof_index_v(i, 0)
            A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0
    elif grid.bc_south == "no_slip":
        for i in range(Nx):
            ku = grid.dof_index_u(i, 0)
            kv = grid.dof_index_v(i, 0)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0
            A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0

    # North: free_slip (v=0) or no_slip (u=0, v=0)
    if grid.bc_north in ("free_slip", "symmetry"):
        for i in range(Nx):
            kv = grid.dof_index_v(i, Ny - 1)
            A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0
    elif grid.bc_north == "no_slip":
        for i in range(Nx):
            ku = grid.dof_index_u(i, Ny - 1)
            kv = grid.dof_index_v(i, Ny - 1)
            A.data[A.indptr[ku]:A.indptr[ku + 1]] = 0.0
            A[ku, ku] = 1.0
            rhs[ku] = 0.0
            A.data[A.indptr[kv]:A.indptr[kv + 1]] = 0.0
            A[kv, kv] = 1.0
            rhs[kv] = 0.0

    A.eliminate_zeros()
    return A, rhs

