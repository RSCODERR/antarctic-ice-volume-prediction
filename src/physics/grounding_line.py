"""
src/physics/grounding_line.py
=============================
Schoof (2007) grounding-line flux parameterisation.

Implements the authoritative boundary-layer solution (Schoof 2007, Eq. 29;
confirmed in Phase 5.0.1 architecture audit and Phase 5.2.2 blueprint):

  q_GL = [ A (ρ_i g)^(n+1) (1 - ρ_i/ρ_w)^n / (4^n C_bed) ]^(1/(m+1)) · H_GL^((m+n+3)/(m+1))

For standard parameters (n = 3, m = 1/3):
  Exponent of base:  1 / (m + 1) = 1 / (4/3) = 3/4 = 0.75
  Exponent of H_GL:  (m + n + 3) / (m + 1) = (1/3 + 3 + 3) / (4/3) = 19/4 = 4.75

Volumetric discharge:
  Q_GL = W_GL · q_GL   [m³ s⁻¹]

Mass flux:
  Ṁ_GL = ρ_i Q_GL   [kg s⁻¹]

Governance:
  - C_bed is the Weertman sliding coefficient [Pa (m s⁻¹)^(-1/3)].
  - Not calibrated against ISMIP6.

Applicability:
  Valid for marine ice sheets terminating in the ocean with floating shelf/ice.
  Land-terminating or narrow-fjord cases: use kinematic flux (W_GL · H_GL · u_GL).

Units:  SI throughout.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import CONST, PhysicsConstants


class SchoofGLFlux:
    """
    Schoof (2007) grounding-line boundary-layer flux.

    Parameters
    ----------
    const : PhysicsConstants
    A : float, optional
        Glen rate factor override [Pa⁻³ s⁻¹].
    C_bed : float, optional
        Basal drag coefficient override [Pa (m s⁻¹)^(-m)].
    m : float, optional
        Weertman exponent override [-].
    """

    def __init__(
        self,
        const: PhysicsConstants = CONST,
        A: float | None = None,
        C_bed: float | None = None,
        m: float | None = None,
    ) -> None:
        self.const = const
        self.n: float = const.glen_n
        self.m: float = m if m is not None else const.weertman_m
        self.A: float = A if A is not None else const.A_default
        self.C_bed: float = C_bed if C_bed is not None else const.C_bed
        self.B: float = self.A ** (-1.0 / self.n)

        # Theoretical exponents
        self.base_exponent: float = 1.0 / (self.m + 1.0)
        self.h_exponent: float = (self.m + self.n + 3.0) / (self.m + 1.0)
        self._prefactor: float = self._compute_prefactor()

    # ------------------------------------------------------------------
    # Prefactor
    # ------------------------------------------------------------------

    def _compute_prefactor(self) -> float:
        """
        Compute the dimensional prefactor of the Schoof GL flux formula.

        base = [ A (ρ_i g)^(n+1) (1 - ρ_i/ρ_w)^n ] / [ 4^n C_bed ]
        prefactor = base^(1 / (m + 1))
        """
        c = self.const
        rho_i = c.rho_ice
        rho_w = c.rho_water
        g = c.g
        n = self.n

        numerator = self.A * ((rho_i * g) ** (n + 1.0)) * ((1.0 - rho_i / rho_w) ** n)
        denominator = (4.0 ** n) * self.C_bed
        base = numerator / denominator

        return float(base ** self.base_exponent)

    # ------------------------------------------------------------------
    # Flux computation
    # ------------------------------------------------------------------

    def q_gl(self, H_GL: float) -> float:
        """
        Schoof grounding-line flux per unit width q_GL [m² s⁻¹].

        q_GL = prefactor · H_GL^h_exponent

        Parameters
        ----------
        H_GL : float
            Ice thickness at the grounding line [m].
        """
        if H_GL <= 0.0:
            return 0.0
        return self._prefactor * (H_GL ** self.h_exponent)

    def Q_gl(self, H_GL: float, W_GL: float) -> float:
        """
        Volumetric grounding-line discharge Q_GL [m³ s⁻¹].

        Q_GL = W_GL · q_GL(H_GL)
        """
        return W_GL * self.q_gl(H_GL)

    def mass_flux(self, H_GL: float, W_GL: float) -> float:
        """
        Mass flux through grounding line Ṁ_GL [kg s⁻¹].

        Ṁ_GL = ρ_i · Q_GL
        """
        return self.const.rho_ice * self.Q_gl(H_GL, W_GL)

    # ------------------------------------------------------------------
    # Kinematic fallback (land-terminating / narrow fjord)
    # ------------------------------------------------------------------

    def Q_kinematic(self, H_GL: float, W_GL: float, u_GL: float) -> float:
        """
        Kinematic grounding-line flux [m³ s⁻¹] for non-Schoof cases.

        Q = W_GL · H_GL · max(0, u_GL)
        """
        return W_GL * H_GL * max(0.0, u_GL)

    # ------------------------------------------------------------------
    # Diagnostic
    # ------------------------------------------------------------------

    def sensitivity(self, H_GL: float, dH: float = 1.0) -> float:
        """
        Sensitivity dq_GL / dH_GL [m s⁻¹].

        = h_exponent · prefactor · H_GL^(h_exponent - 1)
        """
        if H_GL <= 0.0:
            return 0.0
        return self.h_exponent * self._prefactor * (H_GL ** (self.h_exponent - 1.0))

    def __repr__(self) -> str:
        return (
            f"SchoofGLFlux(n={self.n}, m={self.m:.3f}, A={self.A:.2e}, "
            f"C_bed={self.C_bed:.2e}, prefactor={self._prefactor:.4e}, "
            f"h_exp={self.h_exponent:.2f})"
        )
