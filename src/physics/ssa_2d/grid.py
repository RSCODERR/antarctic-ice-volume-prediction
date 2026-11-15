"""
src/physics/ssa_2d/grid.py
==========================
2D structured quadrilateral Cartesian grid for 2D SSA simulations.

Coordinate conventions:
  - x: horizontal along-flow / longitudinal coordinate [m] (indices 0 <= i < Nx)
  - y: horizontal across-flow / transverse coordinate [m] (indices 0 <= j < Ny)
  - 2D arrays are shaped (Ny, Nx) following standard numpy indexing (row j, col i).
"""

from __future__ import annotations
import dataclasses
from typing import Literal
import numpy as np
from numpy.typing import NDArray

BCType = Literal[
    "divide",         # u . n = 0, zero shear stress (symmetry / ice divide)
    "free_slip",      # u . n = 0, zero shear stress
    "no_slip",        # u = 0, v = 0 (Dirichlet rock wall)
    "calving_front",  # MacAyeal depth-integrated normal stress balance
    "dirichlet",      # Prescribed u and v
    "periodic",       # Periodic boundary
]


@dataclasses.dataclass
class Grid2D:
    """
    2D Structured Cartesian grid representation.
    """
    Lx: float
    Ly: float
    Nx: int
    Ny: int
    x0: float = 0.0
    y0: float = 0.0

    bc_west: BCType = "divide"          # x = x0 (i = 0)
    bc_east: BCType = "calving_front"   # x = x0 + Lx (i = Nx - 1)
    bc_south: BCType = "free_slip"      # y = y0 (j = 0)
    bc_north: BCType = "free_slip"      # y = y0 + Ly (j = Ny - 1)

    def __post_init__(self) -> None:
        if self.Nx < 2 or self.Ny < 2:
            raise ValueError(f"Grid must have at least 2 cells in each direction (got Nx={self.Nx}, Ny={self.Ny})")
        if self.Lx <= 0 or self.Ly <= 0:
            raise ValueError(f"Grid dimensions must be positive (got Lx={self.Lx}, Ly={self.Ly})")

        self.dx: float = self.Lx / self.Nx
        self.dy: float = self.Ly / self.Ny

        # 1D coordinates (cell centres)
        self.x_centers: NDArray[np.float64] = self.x0 + (np.arange(self.Nx, dtype=np.float64) + 0.5) * self.dx
        self.y_centers: NDArray[np.float64] = self.y0 + (np.arange(self.Ny, dtype=np.float64) + 0.5) * self.dy

        # 1D coordinates (cell edges / faces)
        self.x_edges: NDArray[np.float64] = self.x0 + np.arange(self.Nx + 1, dtype=np.float64) * self.dx
        self.y_edges: NDArray[np.float64] = self.y0 + np.arange(self.Ny + 1, dtype=np.float64) * self.dy

        # 2D coordinate meshgrids (Ny, Nx)
        self.X, self.Y = np.meshgrid(self.x_centers, self.y_centers)

    @property
    def total_cells(self) -> int:
        return self.Nx * self.Ny

    @property
    def total_dofs(self) -> int:
        """Total degrees of freedom for coupled (u, v) system."""
        return 2 * self.total_cells

    def cell_index(self, i: int, j: int) -> int:
        """Convert 2D cell indices (col i, row j) to 1D flat cell index."""
        if not (0 <= i < self.Nx and 0 <= j < self.Ny):
            raise IndexError(f"Cell indices out of bounds: i={i} (Nx={self.Nx}), j={j} (Ny={self.Ny})")
        return j * self.Nx + i

    def dof_index_u(self, i: int, j: int) -> int:
        """Convert (i, j) to flat DOF index for velocity u."""
        return self.cell_index(i, j)

    def dof_index_v(self, i: int, j: int) -> int:
        """Convert (i, j) to flat DOF index for velocity v."""
        return self.total_cells + self.cell_index(i, j)

    def is_boundary(self, i: int, j: int) -> bool:
        """Check if cell (i, j) is on any external domain boundary."""
        return i == 0 or i == self.Nx - 1 or j == 0 or j == self.Ny - 1

