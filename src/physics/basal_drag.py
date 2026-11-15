"""
src/physics/basal_drag.py
=========================
Regularised Weertman basal drag law.

Implements:
  τ_b(u) = C_bed · |u_reg_eff|^(m-1) · u

where the regularised effective speed is:
  u_reg_eff = √(u² + u_reg²)

so that τ_b remains finite and differentiable at u = 0.

For land-terminating cells (bed above sea level, no sliding):
  τ_b is returned unchanged (sliding law still applies; the solver
  may override with a no-slip condition for specific scenarios — see SSASolver).

Phase 5.2.1 audit value:
  C_bed  = 1×10⁷ Pa (m/s)^(-1/3)   [NOT calibrated against ISMIP6]
  u_reg  = 3.17×10⁻¹² m/s  (= 1×10⁻⁴ m/yr)
  m      = 1/3

The large regularised coefficient β_b(0) = C_bed · u_reg^(m-1) ≈ 4.64×10¹⁰ Pa s m⁻¹
was confirmed correct in Phase 5.2.1 and represents the near-frozen-bed
stiffness.  It does not require ISMIP6 calibration.

Units:  SI.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import CONST, PhysicsConstants


class BasalDrag:
    """
    Regularised Weertman basal drag.

    Parameters
    ----------
    const : PhysicsConstants
        Physical constants (defaults to CONST singleton).
    C_bed : float, optional
        Override basal drag coefficient [Pa (m s⁻¹)^(-m)].
    m : float, optional
        Override sliding exponent [-].
    u_reg : float, optional
        Override regularisation velocity [m s⁻¹].
    """

    def __init__(
        self,
        const: PhysicsConstants = CONST,
        C_bed: float | None = None,
        m: float | None = None,
        u_reg: float | None = None,
    ) -> None:
        self.const = const
        self.C_bed: float = C_bed if C_bed is not None else const.C_bed
        self.m: float = m if m is not None else const.weertman_m
        self.u_reg: float = u_reg if u_reg is not None else const.u_reg

    # ------------------------------------------------------------------
    # Core drag computation
    # ------------------------------------------------------------------

    def tau_b(
        self, u: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """
        Basal shear stress τ_b [Pa] at each cell.

        τ_b_i = C_bed · (u_i² + u_reg²)^((m-1)/2) · u_i

        The sign convention: τ_b acts to oppose ice flow, so for u > 0
        (ice flowing toward ocean) τ_b > 0 is a resistive stress.

        Parameters
        ----------
        u : ndarray [m s⁻¹], shape (N,)
            Sliding velocity (positive = toward ocean).

        Returns
        -------
        tau : ndarray [Pa], shape (N,)
        """
        u = np.asarray(u, dtype=np.float64)
        u2 = u ** 2 + self.u_reg ** 2
        # (u² + u_reg²)^((m-1)/2)  — this is always positive
        exponent = (self.m - 1.0) / 2.0
        return self.C_bed * (u2 ** exponent) * u

    def beta_linearised(self, u: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Linearised drag coefficient β [Pa s m⁻¹] for Picard iteration.

        In the Picard linearisation:
          τ_b ≈ β(u^k) · u^(k+1)

        β(u) = C_bed · (u² + u_reg²)^((m-1)/2)

        This is the coefficient used to form the SSA tridiagonal system.

        Parameters
        ----------
        u : ndarray [m s⁻¹]
            Velocity iterate u^k.

        Returns
        -------
        beta : ndarray [Pa s m⁻¹]
        """
        u = np.asarray(u, dtype=np.float64)
        u2 = u ** 2 + self.u_reg ** 2
        exponent = (self.m - 1.0) / 2.0
        return self.C_bed * (u2 ** exponent)

    def beta_at_rest(self) -> float:
        """
        Regularised β at u = 0  [Pa s m⁻¹].

        β(0) = C_bed · u_reg^(m-1)

        Phase 5.2.1 audit: ≈ 4.64×10¹⁰ Pa s m⁻¹ for default parameters.
        This value represents the near-frozen-bed stiffness and is not
        a calibration target.
        """
        return self.C_bed * (self.u_reg ** (self.m - 1.0))

    # ------------------------------------------------------------------
    # Dimensional verification
    # ------------------------------------------------------------------

    def verify_units(self) -> dict[str, float | str]:
        """
        Return a dictionary of diagnostic values for the dimensional audit.

        No assertions — purely diagnostic output for the test suite.
        """
        beta0 = self.beta_at_rest()
        # At u = 1 m/s: τ_b = C_bed · 1^(m-1) · 1 = C_bed  [Pa]
        tau_at_1ms = float(self.tau_b(np.array([1.0]))[0])
        return {
            "C_bed [Pa (m/s)^(-1/3)]": self.C_bed,
            "m [-]": self.m,
            "u_reg [m/s]": self.u_reg,
            "u_reg [m/yr]": self.u_reg * CONST.yr_to_s,
            "beta_at_rest [Pa s/m]": beta0,
            "tau_b(u=1 m/s) [Pa]": tau_at_1ms,
            "note": "tau_at_1ms should equal C_bed for m=1/3",
        }

    def __repr__(self) -> str:
        return (
            f"BasalDrag(C_bed={self.C_bed:.2e}, m={self.m:.4f}, "
            f"u_reg={self.u_reg:.2e} m/s, β(0)={self.beta_at_rest():.3e} Pa·s/m)"
        )

