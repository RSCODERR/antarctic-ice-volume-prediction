"""
src/physics/rheology.py
=======================
GlensFlowLaw — effective viscosity for the SSA momentum equation.

Implements:
  ν_eff = B / (2 (ε̇_e)^((n-1)/n))

where ε̇_e = √((du/dx)² + ε_reg²) is the regularised effective strain rate.

The Kelvin regularisation ε_reg = 1×10⁻¹⁵ s⁻¹ prevents singular viscosity
at the ice divide.  See Phase 5.2.1 audit.

Units:  SI.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import CONST, PhysicsConstants


class GlensFlowLaw:
    """
    Glen's flow-law viscosity calculator.

    Parameters
    ----------
    const : PhysicsConstants, optional
        Physical constants.  Defaults to the module singleton CONST.
    A : float, optional
        Glen rate factor [Pa⁻³ s⁻¹].  Overrides const.A_default.
    """

    def __init__(
        self,
        const: PhysicsConstants = CONST,
        A: float | None = None,
    ) -> None:
        self.const = const
        self.A: float = A if A is not None else const.A_default
        self.n: float = const.glen_n
        self.eps_reg: float = const.eps_reg_viscosity
        self.B: float = self.A ** (-1.0 / self.n)   # Pa s^(1/n)

    # ------------------------------------------------------------------
    # Core viscosity computation
    # ------------------------------------------------------------------

    def effective_viscosity(
        self, du_dx: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """
        Effective viscosity ν_eff [Pa s] at each cell.

        ν_eff = B / (2 · ε̇_e^((n-1)/n))
        ε̇_e  = √((du/dx)² + ε_reg²)

        Parameters
        ----------
        du_dx : ndarray [s⁻¹]
            Along-flow strain rate at each cell or face.

        Returns
        -------
        nu_eff : ndarray [Pa s]
            Same shape as du_dx.
        """
        du_dx = np.asarray(du_dx, dtype=np.float64)
        eps_e = np.sqrt(du_dx ** 2 + self.eps_reg ** 2)
        exponent = (self.n - 1.0) / self.n   # = 2/3 for n=3
        nu_eff = self.B / (2.0 * eps_e ** exponent)
        return nu_eff

    def effective_viscosity_scalar(self, du_dx: float) -> float:
        """Scalar version for single strain-rate value."""
        eps_e = np.sqrt(du_dx ** 2 + self.eps_reg ** 2)
        exponent = (self.n - 1.0) / self.n
        return float(self.B / (2.0 * eps_e ** exponent))

    # ------------------------------------------------------------------
    # Diagnostic utilities
    # ------------------------------------------------------------------

    def strain_rate_from_velocity(
        self, u: NDArray[np.float64], dx: float
    ) -> NDArray[np.float64]:
        """
        First-order central strain rate from velocity field [s⁻¹].

        du/dx_i ≈ (u_{i+1} - u_{i-1}) / (2 Δx)   (interior)
        Forward/backward difference at boundaries.

        Parameters
        ----------
        u : ndarray [m s⁻¹], shape (N,)
        dx : float [m]

        Returns
        -------
        du_dx : ndarray [s⁻¹], shape (N,)
        """
        du_dx = np.empty_like(u)
        du_dx[1:-1] = (u[2:] - u[:-2]) / (2.0 * dx)
        du_dx[0] = (u[1] - u[0]) / dx
        du_dx[-1] = (u[-1] - u[-2]) / dx
        return du_dx

    def __repr__(self) -> str:
        return (
            f"GlensFlowLaw(n={self.n}, A={self.A:.2e} Pa⁻³ s⁻¹, "
            f"B={self.B:.4e} Pa s^(1/3), ε_reg={self.eps_reg:.0e} s⁻¹)"
        )

