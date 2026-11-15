"""
src/physics/ssa_2d/mismip_plus.py
=================================
MISMIP+ (Marine Ice Sheet Model Intercomparison Project v3) benchmark module.

Implements the official MISMIP+ experimental protocol:
  - Reference: Asay-Davis et al. (2016), Geosci. Model Dev., 9, 2471–2497.
  - Intercomparison: Cornford et al. (2020), The Cryosphere, 14, 2283–2301.

Experiments:
  - Ice0:  Unperturbed steady state under uniform SMB = 0.3 m/a, zero melt.
  - Ice1r: Forced marine retreat under depth-dependent sub-shelf melting for 100 a.
  - Ice1ra: Re-advance / reversibility test after cutting melt to zero for 100 a.
"""

from __future__ import annotations
import dataclasses
import time
import numpy as np
from numpy.typing import NDArray

from .constants import SSA2DConstants, CONST_MISMIP
from .grid import Grid2D
from .friction import compute_flotation_fraction_and_surface
from .solver import SSASolver2D, SSAResult2D
from .continuity import step_continuity_2d, compute_cfl_timestep_2d


def create_mismip_bed(
    grid: Grid2D,
    z_deep: float = -720.0,
) -> NDArray[np.float64]:
    """
    Compute official MISMIP+ bedrock topography b(x, y) [m].

    b(x, y) = max[ B_x(x) + B_y(y), z_deep ]
    """
    x = grid.X  # (Ny, Nx)
    y = grid.Y  # (Ny, Nx)

    # 1. Longitudinal polynomial B_x(x)
    x_tilde = x / 300_000.0
    B0 = -150.0
    B2 = -728.8
    B4 = 343.91
    B6 = -50.75
    B_x = B0 + B2 * (x_tilde ** 2) + B4 * (x_tilde ** 4) + B6 * (x_tilde ** 6)

    # 2. Transverse trough profile B_y(y)
    d_c = 500.0
    w_c = 24_000.0
    f_c = 4_000.0
    y_c = grid.y0 + 0.5 * grid.Ly

    # Two sigmoid walls
    arg1 = -2.0 * (y - y_c - w_c) / f_c
    arg2 = 2.0 * (y - y_c + w_c) / f_c

    # Use stable exp / logistic
    sig1 = 1.0 / (1.0 + np.exp(np.clip(arg1, -50.0, 50.0)))
    sig2 = 1.0 / (1.0 + np.exp(np.clip(arg2, -50.0, 50.0)))
    B_y = d_c * (sig1 + sig2)

    # 3. Superposition with depth cutoff
    bed = np.maximum(B_x + B_y, z_deep)
    return bed


def compute_mismip_melt_rate(
    H: NDArray[np.float64],
    b: NDArray[np.float64],
    f_gr: NDArray[np.float64],
    const: SSA2DConstants = CONST_MISMIP,
    omega_melt: float = 0.2,       # a⁻¹
    H_c0: float = 75.0,            # m
    z_0: float = -100.0,           # m
) -> NDArray[np.float64]:
    """
    Compute MISMIP+ sub-shelf melt rate m_i [m s⁻¹ ice equivalent].

    m_i = Omega * tanh(H_c / H_c0) * max(z_0 - z_d, 0)
    applied strictly on floating ice (1 - f_gr).
    """
    spy = const.sec_per_year
    rho_i = const.rho_ice
    rho_w = const.rho_water

    # Ice shelf draft z_d (negative below sea level)
    z_d = -(rho_i / rho_w) * H

    # Water column thickness H_c = z_d - b
    H_c = np.maximum(z_d - b, 0.0)

    # Thermal forcing: max(z_0 - z_d, 0)
    thermal_drive = np.maximum(z_0 - z_d, 0.0)

    # Water column tapering factor
    cavity_factor = np.tanh(H_c / H_c0)

    # Melt rate in m / yr
    m_ann = omega_melt * cavity_factor * thermal_drive

    # Melt rate in SI [m s⁻¹], zeroed on grounded ice
    m_si = (m_ann / spy) * (1.0 - f_gr)
    return m_si


def find_grounding_line_x(
    f_gr: NDArray[np.float64],
    grid: Grid2D,
    j_row: int | None = None,
) -> float:
    """
    Find along-flow grounding-line position x_GL [m] at a given transverse row (e.g. centerline).
    Uses linear interpolation across the transition cell where f_gr crosses 0.5.
    """
    if j_row is None:
        j_row = grid.Ny // 2

    row_f = f_gr[j_row, :]
    # Find transition from grounded (f_gr ~ 1) to floating (f_gr < 0.5)
    for i in range(grid.Nx - 1):
        if row_f[i] >= 0.5 and row_f[i + 1] < 0.5:
            # Interpolate exact x position
            denom = row_f[i] - row_f[i + 1]
            frac = (row_f[i] - 0.5) / (denom + 1.0e-12)
            x_gl = grid.x_centers[i] + frac * grid.dx
            return float(x_gl)

    # If all grounded or all floating
    if row_f[0] < 0.5:
        return float(grid.x_centers[0])
    return float(grid.x_centers[-1])


def compute_vaf_km3(
    H: NDArray[np.float64],
    b: NDArray[np.float64],
    grid: Grid2D,
    const: SSA2DConstants = CONST_MISMIP,
) -> float:
    """
    Compute official MISMIP+ Volume Above Flotation (VAF) [km³].

    VAF = int_Omega max(0, H + (rho_water / rho_ice) * min(0, b)) dA
    """
    rho_i = const.rho_ice
    rho_w = const.rho_water
    b_sub = np.minimum(0.0, b)
    H_af = np.maximum(0.0, H + (rho_w / rho_i) * b_sub)
    vaf_m3 = float(np.sum(H_af) * grid.dx * grid.dy)
    return vaf_m3 / 1.0e9


def create_mismip_initial_profile(
    grid: Grid2D,
    bed: NDArray[np.float64],
    const: SSA2DConstants = CONST_MISMIP,
    x_gl_target: float = 450_000.0,
    s_divide: float = 1350.0,
    s_cf: float = 35.0,
) -> NDArray[np.float64]:
    """
    Construct a smooth, physically consistent initial thickness field H(x, y) [m]
    targeting mid-channel grounding line at x_gl_target (default 450 km).

    Enforces transverse surface equilibrium (ds/dy ~ 0) to avoid artificial
    cross-channel gravitational driving stress in the curved bed trough.
    """
    x = grid.X
    j_mid = grid.Ny // 2

    # Find bedrock elevation along centerline at target grounding line
    i_gl = int(np.clip(np.round((x_gl_target - grid.x0) / grid.dx), 0, grid.Nx - 1))
    b_gl = float(bed[j_mid, i_gl])

    # Flotation surface elevation at target grounding line
    rho_i = const.rho_ice
    rho_w = const.rho_water
    s_gl = (1.0 - rho_i / rho_w) * (-rho_w / rho_i * b_gl)

    # 1D longitudinal surface elevation profile s_profile(x)
    s_profile = np.zeros_like(x)
    mask_up = x <= x_gl_target
    s_profile[mask_up] = s_divide - (s_divide - s_gl) * (x[mask_up] / x_gl_target)**0.9
    mask_down = x > x_gl_target
    s_profile[mask_down] = s_gl - (s_gl - s_cf) * ((x[mask_down] - x_gl_target) / (grid.Lx - x_gl_target))**0.8

    # Base elevation if floating: z_b_float = - (rho_i / (rho_w - rho_i)) * s_profile
    z_b_float = -(rho_i / (rho_w - rho_i)) * s_profile

    # Where z_b_float < bed: ice is grounded on bedrock -> H = s_profile - bed
    # Where z_b_float >= bed: ice floats in seawater -> H = s_profile / (1.0 - rho_i / rho_w)
    H = np.where(z_b_float < bed, s_profile - bed, s_profile / (1.0 - rho_i / rho_w))
    H = np.maximum(H, 10.0)
    return H


@dataclasses.dataclass
class MISMIPResult:
    experiment: str
    grid: Grid2D
    x_gl_centerline_km: float
    grounded_volume_km3: float
    vaf_km3: float
    max_velocity_m_yr: float
    total_time_yr: float
    runtime_sec: float
    picard_iterations_per_step: list[int]
    hysteresis_offset_m: float | None = None

