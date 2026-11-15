"""
src/physics/ssa_2d/boundary.py
==============================
Boundary condition evaluations for 2D Shallow Shelf Approximation (SSA).

Supported boundary types:
  1. Ice Divide / Symmetry ('divide'):
     - Normal velocity u . n = 0
     - Zero tangential shear stress sigma_nt = 0
  2. Free-Slip ('free_slip'):
     - Normal velocity u . n = 0
     - Zero tangential shear stress sigma_nt = 0
  3. No-Slip Rock Walls ('no_slip'):
     - Homogeneous Dirichlet: u = 0, v = 0
  4. Marine Calving Front ('calving_front'):
     - Depth-integrated normal stress balance (MacAyeal 1989):
         Floating shelf: N_nn = 0.5 * rho_i * g * H^2 * (1 - rho_i / rho_water)
         Tidewater cliff: N_nn = 0.5 * rho_i * g * H^2 - 0.5 * rho_water * g * d_w^2
     - Zero tangential shear traction: N_nt = 0
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import SSA2DConstants, CONST_DEFAULT
from .grid import Grid2D


def compute_calving_front_traction(
    H_front: NDArray[np.float64],
    b_front: NDArray[np.float64],
    is_floating: NDArray[np.bool_],
    const: SSA2DConstants = CONST_DEFAULT,
) -> NDArray[np.float64]:
    """
    Compute depth-integrated normal stress N_nn [N m⁻¹ = Pa m] at a marine calving front.

    Parameters
    ----------
    H_front : NDArray[np.float64]
        Ice thickness at front [m] (shape: (Ny,)).
    b_front : NDArray[np.float64]
        Bedrock elevation at front [m] (shape: (Ny,)).
    is_floating : NDArray[np.bool_]
        Boolean array indicating whether front cells are floating.
    const : SSA2DConstants

    Returns
    -------
    N_nn : NDArray[np.float64]
        Depth-integrated normal tensile stress [N m⁻¹] along the calving front.
    """
    rho_i = const.rho_ice
    rho_w = const.rho_water
    g = const.g

    N_nn = np.zeros_like(H_front, dtype=np.float64)

    # 1. Floating shelf calving front
    # N_nn = 0.5 * rho_i * g * H^2 * (1 - rho_i / rho_w)
    float_idx = is_floating
    if np.any(float_idx):
        Hf = H_front[float_idx]
        N_nn[float_idx] = 0.5 * rho_i * g * (Hf ** 2) * (1.0 - (rho_i / rho_w))

    # 2. Grounded tidewater calving cliff
    # Terminating in water depth d_w = max(0, -b)
    ground_idx = ~is_floating
    if np.any(ground_idx):
        Hg = H_front[ground_idx]
        bg = b_front[ground_idx]
        d_w = np.maximum(0.0, -bg)
        N_nn[ground_idx] = 0.5 * rho_i * g * (Hg ** 2) - 0.5 * rho_w * g * (d_w ** 2)

    return N_nn

