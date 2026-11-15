"""
src/physics/ssa_2d/rheology.py
==============================
Ice rheology and non-linear effective viscosity based on Glen's flow law (n=3).

Formulations:
  - Strain rates:
      eps_xx = du/dx
      eps_yy = dv/dy
      eps_xy = 0.5 * (du/dy + dv/dx)
  - Effective strain rate invariant:
      eps_e^2 = eps_xx^2 + eps_yy^2 + eps_xx * eps_yy + eps_xy^2 + eps_0^2
  - Depth-averaged effective viscosity (Glen's law with n=3):
      nu_eff = 0.5 * A^(-1/n) * (eps_e^2)^((1-n)/(2n))
             = 0.5 * A^(-1/3) * (eps_e^2)^(-1/3)
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import SSA2DConstants, CONST_DEFAULT
from .grid import Grid2D


def compute_strain_rates_2d(
    u: NDArray[np.float64],
    v: NDArray[np.float64],
    grid: Grid2D,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Compute horizontal strain rates (eps_xx, eps_yy, eps_xy) on cell centres (Ny, Nx).

    Uses second-order central differences on the interior and appropriate
    one-sided or ghost-cell differences at domain boundaries.
    """
    Ny, Nx = grid.Ny, grid.Nx
    dx, dy = grid.dx, grid.dy

    eps_xx = np.zeros((Ny, Nx), dtype=np.float64)
    eps_yy = np.zeros((Ny, Nx), dtype=np.float64)
    du_dy = np.zeros((Ny, Nx), dtype=np.float64)
    dv_dx = np.zeros((Ny, Nx), dtype=np.float64)

    # du/dx: interior central difference
    eps_xx[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2.0 * dx)
    # du/dx: boundaries
    if grid.bc_west in ("divide", "free_slip"):
        # Normal velocity u = 0 at west boundary edge x=0
        # Edge value u(0) = 0. Distance from center 0 to edge is dx/2.
        # eps_xx[:, 0] = (u[:, 0] - 0) / (dx / 2) = 2 * u[:, 0] / dx
        eps_xx[:, 0] = (u[:, 1] - u[:, 0]) / dx
    else:
        eps_xx[:, 0] = (u[:, 1] - u[:, 0]) / dx
    eps_xx[:, -1] = (u[:, -1] - u[:, -2]) / dx

    # dv/dy: interior central difference
    eps_yy[1:-1, :] = (v[2:, :] - v[:-2, :]) / (2.0 * dy)
    eps_yy[0, :] = (v[1, :] - v[0, :]) / dy
    eps_yy[-1, :] = (v[-1, :] - v[-2, :]) / dy

    # du/dy: interior central difference
    du_dy[1:-1, :] = (u[2:, :] - u[:-2, :]) / (2.0 * dy)
    if grid.bc_south in ("free_slip", "symmetry"):
        # Zero shear du/dy = 0 at south boundary
        du_dy[0, :] = 0.0
    elif grid.bc_south == "no_slip":
        # Rock wall u = 0 at y=0 edge
        du_dy[0, :] = (u[1, :] - 0.0) / (1.5 * dy)
    else:
        du_dy[0, :] = (u[1, :] - u[0, :]) / dy

    if grid.bc_north in ("free_slip", "symmetry"):
        du_dy[-1, :] = 0.0
    elif grid.bc_north == "no_slip":
        du_dy[-1, :] = (0.0 - u[-2, :]) / (1.5 * dy)
    else:
        du_dy[-1, :] = (u[-1, :] - u[-2, :]) / dy

    # dv/dx: interior central difference
    dv_dx[:, 1:-1] = (v[:, 2:] - v[:, :-2]) / (2.0 * dx)
    if grid.bc_west in ("divide", "free_slip"):
        dv_dx[:, 0] = 0.0  # Zero shear dv/dx = 0 at divide
    else:
        dv_dx[:, 0] = (v[:, 1] - v[:, 0]) / dx
    dv_dx[:, -1] = (v[:, -1] - v[:, -2]) / dx

    eps_xy = 0.5 * (du_dy + dv_dx)

    return eps_xx, eps_yy, eps_xy


def compute_effective_strain_rate_sq(
    eps_xx: NDArray[np.float64],
    eps_yy: NDArray[np.float64],
    eps_xy: NDArray[np.float64],
    eps_0: float = 1.0e-10,
) -> NDArray[np.float64]:
    """
    Compute second invariant of strain rate tensor:
    eps_e^2 = eps_xx^2 + eps_yy^2 + eps_xx * eps_yy + eps_xy^2 + eps_0^2
    """
    return eps_xx**2 + eps_yy**2 + eps_xx * eps_yy + eps_xy**2 + eps_0**2


def compute_effective_viscosity_2d(
    u: NDArray[np.float64],
    v: NDArray[np.float64],
    grid: Grid2D,
    const: SSA2DConstants = CONST_DEFAULT,
) -> NDArray[np.float64]:
    """
    Compute 2D depth-averaged effective viscosity [Pa s] at cell centres.
    """
    eps_xx, eps_yy, eps_xy = compute_strain_rates_2d(u, v, grid)
    eps_e_sq = compute_effective_strain_rate_sq(eps_xx, eps_yy, eps_xy, eps_0=const.eps_0)

    n = const.glen_n
    exponent = (1.0 - n) / (2.0 * n)  # -1/3 for n=3
    B = const.glen_A ** (-1.0 / n)      # Pa s^(1/3)
    nu = 0.5 * B * (eps_e_sq ** exponent)
    return nu

