"""
src/physics/ssa_2d/friction.py
==============================
Basal sliding and sub-grid grounding-line flotation routines.

Formulations:
  - Flotation condition:
      H_flot = - (rho_water / rho_ice) * min(0, b)
      Phi = rho_ice * H + rho_water * min(0, b)
      If Phi > 0: cell is grounded.
      If Phi <= 0: cell is floating.
  - Sub-grid grounded fraction f_gr in [0, 1].
  - Surface elevation s(x, y):
      Grounded: s = b + H
      Floating: s = (1 - rho_ice / rho_water) * H
      Sub-grid: s = f_gr * (b + H) + (1 - f_gr) * (1 - rho_ice / rho_water) * H
  - Weertman non-linear sliding drag coefficient:
      beta_b = f_gr * C_bed * (u^2 + v^2 + u_0^2)^((m - 1)/2)
      where m = 1/3, beta_b in [Pa s m⁻¹].
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import SSA2DConstants, CONST_DEFAULT
from .grid import Grid2D


def compute_flotation_fraction_and_surface(
    H: NDArray[np.float64],
    b: NDArray[np.float64],
    const: SSA2DConstants = CONST_DEFAULT,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Compute sub-grid grounded fraction f_gr in [0, 1], flotation thickness H_flot,
    and continuous surface elevation s(x, y).

    Parameters
    ----------
    H : NDArray[np.float64]
        Ice thickness [m] (Ny, Nx).
    b : NDArray[np.float64]
        Bedrock elevation [m] (Ny, Nx).
    const : SSA2DConstants

    Returns
    -------
    f_gr : NDArray[np.float64]
        Sub-grid grounded area fraction in [0, 1].
    s : NDArray[np.float64]
        Surface elevation [m].
    H_flot : NDArray[np.float64]
        Flotation thickness [m].
    """
    rho_i = const.rho_ice
    rho_w = const.rho_water
    density_ratio = rho_i / rho_w

    # Bedrock where submerged below sea level (z = 0)
    b_sub = np.minimum(b, 0.0)
    H_flot = -b_sub / density_ratio

    # Height above flotation: Phi_h = H - H_flot [m]
    Phi_h = H - H_flot

    # Grounded fraction: fully grounded if Phi_h > 0, floating if <= 0
    # For sub-grid interpolation (SEP3 standard):
    # If cell is grounded (Phi_h > 0) but adjacent cell is floating (Phi_h < 0),
    # fraction is clamped ratio.
    f_gr = np.zeros_like(H, dtype=np.float64)
    grounded_mask = Phi_h > 0.0
    f_gr[grounded_mask] = 1.0

    # Smooth sub-grid transition at grounding line
    # For 1D/2D cells next to floating cells:
    # subgrid fraction f_gr = clip(Phi_h / (H * (1 - density_ratio)), 0, 1) if within transition
    transition_width = 10.0  # 10m buffer zone for subgrid interpolation
    transition_mask = (Phi_h >= -transition_width) & (Phi_h <= transition_width)
    f_gr[transition_mask] = np.clip(
        0.5 + 0.5 * (Phi_h[transition_mask] / transition_width),
        0.0,
        1.0,
    )
    # Ensure purely floating regions remain exactly 0
    f_gr[Phi_h < -transition_width] = 0.0
    f_gr[Phi_h > transition_width] = 1.0

    # Surface elevation s
    # Grounded surface: s_gr = b + H
    # Floating surface: s_fl = (1.0 - density_ratio) * H
    s_gr = b + H
    s_fl = (1.0 - density_ratio) * H
    s = f_gr * s_gr + (1.0 - f_gr) * s_fl

    return f_gr, s, H_flot


def compute_basal_drag_coefficient(
    u: NDArray[np.float64],
    v: NDArray[np.float64],
    f_gr: NDArray[np.float64],
    C_bed: float | NDArray[np.float64],
    const: SSA2DConstants = CONST_DEFAULT,
) -> NDArray[np.float64]:
    """
    Compute non-linear Weertman basal drag coefficient beta_b [Pa s m⁻¹]:
    beta_b = f_gr * C_bed * (u^2 + v^2 + u_0^2)^((m - 1)/2)
    where m = 1/3.
    """
    m = const.weertman_m
    u_0 = const.u_0
    vel_sq = u**2 + v**2 + u_0**2
    exponent = (m - 1.0) / 2.0  # (1/3 - 1)/2 = -1/3 for m=1/3

    beta_b = f_gr * C_bed * (vel_sq ** exponent)
    return beta_b

