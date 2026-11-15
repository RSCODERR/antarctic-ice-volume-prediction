"""
src/physics/state.py
====================
IceState — the complete mutable state vector for one flowline at one timestep.

The state is intentionally a plain dataclass (no hidden buffers, no lazy fields)
so that tests can construct arbitrary states and inspect every variable directly.

Mass-budget ledger
------------------
Two separate ledgers are maintained and are NEVER merged:
  grounded_mass_kg   — Σ ρ_i W_i Δx H_i  over grounded cells
  floating_mass_kg   — mass of floating ice within the domain

Both ledgers must be updated simultaneously on every retreat/advance event.
Any discrepancy between the ledger sum and the cell-level sum triggers a
hard conservation error (not a silent correction).

Units:  SI throughout.
"""

from __future__ import annotations
import dataclasses
import numpy as np
from numpy.typing import NDArray

from .constants import CONST


@dataclasses.dataclass
class IceState:
    """
    State vector for one 1-D flowline at time t.

    Parameters
    ----------
    H : ndarray, shape (N,)
        Ice thickness [m] for all N cells (both grounded and floating tracked
        here, though only grounded cells are evolved by the SSA solver).
    bed : ndarray, shape (N,)
        Bed elevation z_b [m above sea level, negative below].  Frozen field.
    width : ndarray, shape (N,)
        Flow-tube width W [m] at each cell centre.  Frozen field.
    x_centres : ndarray, shape (N,)
        Along-flow position of cell centres [m] from upstream divide.
    gl_cell : int
        Index of the terminal (partially-grounded) cell, g(n).
    gl_frac : float
        Partial-cell fraction λ_g ∈ (0, 1].  λ_g = 1 means the cell is
        fully grounded (GL lies at its downstream face).
    t : float
        Current model time [s].
    floating_mass_kg : float
        Floating-ice-reservoir ledger [kg].  Must be updated whenever cells
        transition between grounded and floating.
    sea_level : float
        Current sea-level elevation [m above datum].  Default 0.0.
    """

    H: NDArray[np.float64]
    bed: NDArray[np.float64]
    width: NDArray[np.float64]
    x_centres: NDArray[np.float64]
    gl_cell: int
    gl_frac: float
    t: float
    floating_mass_kg: float
    sea_level: float = 0.0

    # ------------------------------------------------------------------
    # Derived geometry
    # ------------------------------------------------------------------

    @property
    def N(self) -> int:
        """Total number of cells in the domain."""
        return len(self.H)

    @property
    def dx(self) -> float:
        """Grid spacing [m].  Uniform; asserted equal to CONST.domain_dx."""
        if self.N < 2:
            return CONST.domain_dx
        return float(self.x_centres[1] - self.x_centres[0])

    @property
    def x_gl(self) -> float:
        """Grounding-line position [m] from divide."""
        g = self.gl_cell
        return self.x_centres[g] - 0.5 * self.dx + self.gl_frac * self.dx

    @property
    def n_grounded(self) -> int:
        """Number of fully- or partially-grounded cells."""
        return self.gl_cell + 1

    @property
    def H_gl(self) -> float:
        """Ice thickness at the grounding line [m]  (terminal cell value)."""
        return float(self.H[self.gl_cell])

    @property
    def W_gl(self) -> float:
        """Width at the grounding line [m]."""
        return float(self.width[self.gl_cell])

    # ------------------------------------------------------------------
    # Mass accounting
    # ------------------------------------------------------------------

    def compute_grounded_mass_kg(self) -> float:
        """
        Compute grounded ice mass from the thickness field [kg].

        Uses the partial-cell fraction for the terminal cell.

        M_gr = ρ_i Σ_{i=0}^{g-1} W_i Δx H_i  +  ρ_i W_g λ_g Δx H_g
        """
        dx = self.dx
        g = self.gl_cell
        # Interior fully-grounded cells
        mass_interior = float(
            np.sum(self.width[:g] * self.H[:g]) * dx * CONST.rho_ice
        )
        # Terminal partial cell
        mass_terminal = (
            self.width[g] * self.gl_frac * dx * self.H[g] * CONST.rho_ice
        )
        return mass_interior + mass_terminal

    def flotation_mask(self) -> NDArray[np.bool_]:
        """
        Boolean mask: True where ice is floating (H < H_crit).

        H_crit_i = (ρ_w / ρ_i) · max(0, z_sl − z_b_i)
        """
        H_crit = (CONST.rho_water / CONST.rho_ice) * np.maximum(
            0.0, self.sea_level - self.bed
        )
        return self.H < H_crit

    def assert_domain_frozen(self) -> None:
        """
        Assert that the grid spacing matches the frozen Phase 2.6 baseline.

        Raises AssertionError if violated.  Call at initialisation.
        """
        assert abs(self.dx - CONST.domain_dx) < 1.0, (
            f"Grid spacing {self.dx:.1f} m ≠ frozen baseline "
            f"{CONST.domain_dx:.0f} m.  Domain A must not be modified."
        )

    def assert_gl_valid(self) -> None:
        """Check that gl_cell and gl_frac are internally consistent."""
        assert 0 <= self.gl_cell < self.N, (
            f"gl_cell={self.gl_cell} out of range [0, {self.N})."
        )
        assert 0.0 < self.gl_frac <= 1.0 + 1e-12, (
            f"gl_frac={self.gl_frac:.6f} not in (0, 1]."
        )

    def assert_no_negative_thickness(self) -> None:
        """Hard-fail if any cell has negative ice thickness."""
        if np.any(self.H < 0.0):
            neg_idx = np.where(self.H < 0.0)[0]
            raise ValueError(
                f"Negative ice thickness in {len(neg_idx)} cells. "
                f"First violation: cell {neg_idx[0]}, H = {self.H[neg_idx[0]]:.4f} m."
            )

    def copy(self) -> "IceState":
        """Return a deep copy suitable for use as the next-step state."""
        return IceState(
            H=self.H.copy(),
            bed=self.bed.copy(),
            width=self.width.copy(),
            x_centres=self.x_centres.copy(),
            gl_cell=self.gl_cell,
            gl_frac=self.gl_frac,
            t=self.t,
            floating_mass_kg=self.floating_mass_kg,
            sea_level=self.sea_level,
        )

    def __repr__(self) -> str:
        return (
            f"IceState(N={self.N}, t={self.t * CONST.s_to_yr:.3f} yr, "
            f"gl_cell={self.gl_cell}, gl_frac={self.gl_frac:.4f}, "
            f"x_GL={self.x_gl / 1e3:.2f} km, "
            f"H_GL={self.H_gl:.1f} m, "
            f"M_gr={self.compute_grounded_mass_kg() * CONST.kg_to_Gt:.4f} Gt)"
        )

