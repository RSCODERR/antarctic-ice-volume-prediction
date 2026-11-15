"""
src/physics/ssa_2d/continuity.py
================================
2D Finite-Volume ice thickness continuity solver.

Solves the hyperbolic mass balance conservation equation:
  dH/dt + d(H u)/dx + d(H v)/dy = SMB - M_shelf

Discretization:
  - First-order upwind finite-volume flux formulation.
  - Rigorous discrete mass conservation tracking:
      Residual = | (M(t+dt) - M(t)) - dt * (Total_SMB - Outflow) |
  - Automatic CFL timestep safety constraint calculation.
"""

from __future__ import annotations
import dataclasses
import numpy as np
from numpy.typing import NDArray

from .constants import SSA2DConstants, CONST_DEFAULT
from .grid import Grid2D


@dataclasses.dataclass
class ContinuityResult2D:
    H_next: NDArray[np.float64]         # Updated thickness [m]
    flux_x: NDArray[np.float64]         # x-direction face fluxes [m² s⁻¹] (Ny, Nx + 1)
    flux_y: NDArray[np.float64]         # y-direction face fluxes [m² s⁻¹] (Ny + 1, Nx)
    net_inflow_mass_kg: float           # Net SMB / melt mass input [kg]
    net_outflow_mass_kg: float          # Mass lost through domain boundary boundaries [kg]
    mass_change_kg: float               # Discrete M(t+dt) - M(t) [kg]
    conservation_error_kg: float        # Absolute mass error [kg]
    relative_error: float               # Relative mass error


def compute_cfl_timestep_2d(
    u: NDArray[np.float64],
    v: NDArray[np.float64],
    grid: Grid2D,
    cfl_factor: float = 0.5,
) -> float:
    """
    Compute maximum allowable CFL timestep [s] for explicit thickness advection:
      dt_cfl = cfl_factor * min(dx / max|u|, dy / max|v|)
    """
    max_u = float(np.max(np.abs(u)))
    max_v = float(np.max(np.abs(v)))

    dt_x = grid.dx / (max_u + 1.0e-12)
    dt_y = grid.dy / (max_v + 1.0e-12)
    return float(cfl_factor * min(dt_x, dt_y))


def step_continuity_2d(
    H: NDArray[np.float64],
    u: NDArray[np.float64],
    v: NDArray[np.float64],
    grid: Grid2D,
    dt: float,
    smb: NDArray[np.float64] | float = 0.0,
    m_shelf: NDArray[np.float64] | float = 0.0,
    const: SSA2DConstants = CONST_DEFAULT,
) -> ContinuityResult2D:
    """
    Advance ice thickness by time step dt using 2D upwind finite volume.

    Parameters
    ----------
    H : NDArray[np.float64]
        Ice thickness at time t [m] (Ny, Nx).
    u : NDArray[np.float64]
        Velocity u [m s⁻¹] (Ny, Nx).
    v : NDArray[np.float64]
        Velocity v [m s⁻¹] (Ny, Nx).
    grid : Grid2D
    dt : float
        Time step [s].
    smb : NDArray[np.float64] | float
        Surface mass balance rate [m s⁻¹ ice equivalent].
    m_shelf : NDArray[np.float64] | float
        Basal melt rate beneath floating ice [m s⁻¹ ice equivalent].
    const : SSA2DConstants

    Returns
    -------
    ContinuityResult2D
    """
    Nx, Ny = grid.Nx, grid.Ny
    dx, dy = grid.dx, grid.dy
    rho_i = const.rho_ice
    cell_area = dx * dy

    # Initial total mass
    mass_0 = float(np.sum(H) * rho_i * cell_area)

    # Convert smb and m_shelf to 2D arrays if scalar
    if np.isscalar(smb):
        smb_arr = np.full((Ny, Nx), float(smb), dtype=np.float64)
    else:
        smb_arr = np.asarray(smb, dtype=np.float64)

    if np.isscalar(m_shelf):
        m_shelf_arr = np.full((Ny, Nx), float(m_shelf), dtype=np.float64)
    else:
        m_shelf_arr = np.asarray(m_shelf, dtype=np.float64)

    # 1. Compute x-fluxes at faces i - 1/2 for i = 0 .. Nx (shape: Ny, Nx + 1)
    flux_x = np.zeros((Ny, Nx + 1), dtype=np.float64)

    # Interior x-faces (i = 1 .. Nx - 1)
    u_face_x = 0.5 * (u[:, :-1] + u[:, 1:])
    H_upwind_x = np.where(u_face_x >= 0.0, H[:, :-1], H[:, 1:])
    flux_x[:, 1:-1] = u_face_x * H_upwind_x

    # West boundary face (i = 0)
    if grid.bc_west in ("divide", "free_slip", "no_slip"):
        flux_x[:, 0] = 0.0  # Zero normal flux
    elif grid.bc_west == "periodic":
        u_face_w = 0.5 * (u[:, -1] + u[:, 0])
        H_upwind_w = np.where(u_face_w >= 0.0, H[:, -1], H[:, 0])
        flux_x[:, 0] = u_face_w * H_upwind_w
    else:
        flux_x[:, 0] = u[:, 0] * H[:, 0]

    # East boundary face (i = Nx)
    if grid.bc_east in ("calving_front", "dirichlet"):
        # Outgoing flux from last cell
        u_east = u[:, -1]
        flux_x[:, -1] = np.where(u_east >= 0.0, u_east * H[:, -1], 0.0)
    elif grid.bc_east == "periodic":
        flux_x[:, -1] = flux_x[:, 0]
    elif grid.bc_east in ("free_slip", "no_slip"):
        flux_x[:, -1] = 0.0

    # 2. Compute y-fluxes at faces j - 1/2 for j = 0 .. Ny (shape: Ny + 1, Nx)
    flux_y = np.zeros((Ny + 1, Nx), dtype=np.float64)

    # Interior y-faces (j = 1 .. Ny - 1)
    v_face_y = 0.5 * (v[:-1, :] + v[1:, :])
    H_upwind_y = np.where(v_face_y >= 0.0, H[:-1, :], H[1:, :])
    flux_y[1:-1, :] = v_face_y * H_upwind_y

    # South boundary face (j = 0)
    if grid.bc_south in ("free_slip", "no_slip", "symmetry"):
        flux_y[0, :] = 0.0
    elif grid.bc_south == "periodic":
        v_face_s = 0.5 * (v[-1, :] + v[0, :])
        H_upwind_s = np.where(v_face_s >= 0.0, H[-1, :], H[0, :])
        flux_y[0, :] = v_face_s * H_upwind_s
    else:
        flux_y[0, :] = v[0, :] * H[0, :]

    # North boundary face (j = Ny)
    if grid.bc_north in ("free_slip", "no_slip", "symmetry"):
        flux_y[-1, :] = 0.0
    elif grid.bc_north == "periodic":
        flux_y[-1, :] = flux_y[0, :]
    else:
        flux_y[-1, :] = v[-1, :] * H[-1, :]

    # 3. Finite volume update
    # div(q) = (flux_x_{i+1/2} - flux_x_{i-1/2}) / dx + (flux_y_{j+1/2} - flux_y_{j-1/2}) / dy
    div_q = (flux_x[:, 1:] - flux_x[:, :-1]) / dx + (flux_y[1:, :] - flux_y[:-1, :]) / dy
    source_rate = smb_arr - m_shelf_arr

    H_next = H - dt * div_q + dt * source_rate
    H_next = np.maximum(H_next, 0.0)

    # 4. Strict mass balance tracking
    mass_1 = float(np.sum(H_next) * rho_i * cell_area)
    mass_change = mass_1 - mass_0

    # Total mass in through source (kg)
    net_inflow_mass = float(np.sum(source_rate) * rho_i * cell_area * dt)

    # Total mass out through boundaries (kg)
    # flux_x[:, -1] has units [m² s⁻¹]. Integrated over lateral height dy: flux [m³ s⁻¹].
    outflow_east = float(np.sum(flux_x[:, -1]) * dy * rho_i * dt)
    inflow_west = float(np.sum(flux_x[:, 0]) * dy * rho_i * dt)
    outflow_north = float(np.sum(flux_y[-1, :]) * dx * rho_i * dt)
    inflow_south = float(np.sum(flux_y[0, :]) * dx * rho_i * dt)

    net_boundary_outflow = (outflow_east - inflow_west) + (outflow_north - inflow_south)
    expected_mass_change = net_inflow_mass - net_boundary_outflow

    conservation_error = abs(mass_change - expected_mass_change)
    rel_error = conservation_error / (mass_0 + 1.0e-12)

    return ContinuityResult2D(
        H_next=H_next,
        flux_x=flux_x,
        flux_y=flux_y,
        net_inflow_mass_kg=net_inflow_mass,
        net_outflow_mass_kg=net_boundary_outflow,
        mass_change_kg=mass_change,
        conservation_error_kg=conservation_error,
        relative_error=rel_error,
    )

