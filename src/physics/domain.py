"""
src/physics/domain.py
=====================
FlowlineDomain — geometry initialisation for a 1-D Peninsula flowline.

This module creates the fixed spatial grid and loads or synthesises the
bed topography and flow-tube width from the frozen Phase 2.6 BedMachine V4.1
processed data.

The Domain A frozen constraints are enforced here:
  Δx = 500 m   (CONST.domain_dx)
  Total grounded cells ≤ CONST.domain_n_cells  (866 358)

For Stage 1 testing, synthetic analytic geometries are provided via
`FlowlineDomain.synthetic()` so that tests do not require the raw data files.

Units:  SI.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Optional

from .constants import CONST
from .state import IceState


class FlowlineDomain:
    """
    Geometry container for one 1-D flowline.

    Parameters
    ----------
    x_centres : ndarray [m]
        Along-flow positions of cell centres (monotone increasing from divide).
    bed : ndarray [m]
        Bed elevation z_b at each cell centre (negative = below sea level).
    width : ndarray [m]
        Flow-tube width W at each cell centre.
    H_init : ndarray [m]
        Initial ice thickness.
    name : str
        Human-readable flowline identifier (e.g. "Hp-I_flowline_01").
    source : str
        Provenance string (e.g. "BedMachine_V4.1_synthetic").
    """

    def __init__(
        self,
        x_centres: NDArray[np.float64],
        bed: NDArray[np.float64],
        width: NDArray[np.float64],
        H_init: NDArray[np.float64],
        name: str = "unnamed",
        source: str = "unspecified",
    ) -> None:
        x_centres = np.asarray(x_centres, dtype=np.float64)
        bed = np.asarray(bed, dtype=np.float64)
        width = np.asarray(width, dtype=np.float64)
        H_init = np.asarray(H_init, dtype=np.float64)

        N = len(x_centres)
        assert len(bed) == N, "bed length mismatch"
        assert len(width) == N, "width length mismatch"
        assert len(H_init) == N, "H_init length mismatch"
        assert N > 2, "Domain must have at least 3 cells"
        assert np.all(width > 0), "All widths must be positive"
        assert np.all(H_init >= 0), "Initial thickness must be non-negative"

        # Verify grid spacing is uniform and matches frozen baseline
        dx_arr = np.diff(x_centres)
        assert np.allclose(dx_arr, CONST.domain_dx, rtol=1e-6), (
            f"Non-uniform or incorrect Δx detected.  "
            f"All spacings must equal {CONST.domain_dx:.0f} m."
        )

        self.x_centres = x_centres
        self.bed = bed
        self.width = width
        self.H_init = H_init
        self.name = name
        self.source = source
        self.N = N
        self.dx = CONST.domain_dx

    # ------------------------------------------------------------------
    # Harmonic-mean face widths
    # ------------------------------------------------------------------

    @property
    def width_faces(self) -> NDArray[np.float64]:
        """
        Harmonic-mean widths at cell faces  W_{i+½}  [m].

        W_{i+½} = 2 W_i W_{i+1} / (W_i + W_{i+1})

        Shape: (N-1,).  Face i+½ lies between cells i and i+1.
        Prevents spurious flux divergence at sharp width transitions
        (Phase 5.2.2.2 FV derivation).
        """
        W = self.width
        return 2.0 * W[:-1] * W[1:] / (W[:-1] + W[1:])

    # ------------------------------------------------------------------
    # Initial IceState
    # ------------------------------------------------------------------

    def initial_state(
        self,
        t0: float = 0.0,
        sea_level: float = 0.0,
        floating_mass_kg: float = 0.0,
    ) -> IceState:
        """
        Construct the initial IceState from this domain geometry.

        The grounding line is placed at the last cell where the ice is grounded
        (H > H_crit).  Sub-cell fraction is set to 1.0 (GL at downstream face).

        Parameters
        ----------
        t0 : float
            Initial time [s].
        sea_level : float
            Initial sea level [m].
        floating_mass_kg : float
            Initial floating reservoir mass [kg].  Default 0 for synthetic tests.
        """
        H = self.H_init.copy()
        H_crit = (CONST.rho_water / CONST.rho_ice) * np.maximum(
            0.0, sea_level - self.bed
        )
        grounded = H >= H_crit

        # Find terminal grounded cell
        grounded_indices = np.where(grounded)[0]
        if len(grounded_indices) == 0:
            raise ValueError("No grounded cells in initial state.")
        gl_cell = int(grounded_indices[-1])
        gl_frac = 1.0  # GL at downstream face of last grounded cell

        state = IceState(
            H=H,
            bed=self.bed.copy(),
            width=self.width.copy(),
            x_centres=self.x_centres.copy(),
            gl_cell=gl_cell,
            gl_frac=gl_frac,
            t=t0,
            floating_mass_kg=floating_mass_kg,
            sea_level=sea_level,
        )
        state.assert_domain_frozen()
        state.assert_gl_valid()
        return state

    # ------------------------------------------------------------------
    # Factory: synthetic analytic geometry
    # ------------------------------------------------------------------

    @classmethod
    def synthetic(
        cls,
        N: int = 200,
        L: float = 100_000.0,
        bed_slope: float = -0.001,
        bed_offset: float = 500.0,
        width_m: float = 20_000.0,
        H0: float = 500.0,
        name: str = "synthetic_flat",
    ) -> "FlowlineDomain":
        """
        Create a synthetic flowline domain for testing.

        Geometry:
          x  = 0, Δx, 2Δx, …  (uniform grid)
          z_b = bed_offset + bed_slope · x   (ramp, positive = above sea level)
          W  = width_m  (constant)
          H  = H0  (uniform initial thickness)

        Parameters
        ----------
        N : int
            Number of cells.  Δx is inferred as L/N, rounded to 500 m.
        L : float
            Total flowline length [m].
        bed_slope : float
            Bed slope dz/dx [m m⁻¹].  Negative = down-sloping toward ocean.
        bed_offset : float
            Bed elevation at x=0 [m above sea level].
        width_m : float
            Constant width [m].
        H0 : float
            Uniform initial ice thickness [m].
        name : str
            Identifier string.
        """
        # Force Δx = 500 m
        dx = CONST.domain_dx
        N_actual = max(3, int(round(L / dx)))
        x = np.arange(N_actual, dtype=np.float64) * dx + 0.5 * dx  # cell centres
        bed = bed_offset + bed_slope * x
        width = np.full(N_actual, width_m, dtype=np.float64)
        H = np.full(N_actual, H0, dtype=np.float64)
        return cls(x, bed, width, H, name=name, source="synthetic_analytic")

    @classmethod
    def synthetic_marine(
        cls,
        N_land: int = 50,
        N_marine: int = 100,
        width_m: float = 20_000.0,
        H0: float = 400.0,
        name: str = "synthetic_marine",
    ) -> "FlowlineDomain":
        """
        Synthetic flowline with land portion then marine bed below sea level.

        z_b transitions from +200 m at divide to -600 m at terminus.
        Provides a realistic grounding-line environment for FGE-FR tests.
        """
        dx = CONST.domain_dx
        N = N_land + N_marine
        x = np.arange(N, dtype=np.float64) * dx + 0.5 * dx
        # Bed: linearly interpolated from +200 to -600 m
        bed = np.linspace(200.0, -600.0, N)
        width = np.full(N, width_m, dtype=np.float64)
        H = np.full(N, H0, dtype=np.float64)
        return cls(x, bed, width, H, name=name, source="synthetic_marine")

    def __repr__(self) -> str:
        return (
            f"FlowlineDomain('{self.name}', N={self.N}, "
            f"L={self.x_centres[-1] / 1e3:.1f} km, "
            f"Δx={self.dx:.0f} m, source='{self.source}')"
        )

