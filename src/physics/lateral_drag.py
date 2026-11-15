"""
src/physics/lateral_drag.py
===========================
Lateral (rock-wall) drag for the 1-D SSA.

Implements the formula confirmed correct in Phase 5.2.2.5:

  τ_wall = (5 ū / (A W))^(1/n)

where:
  ū  = depth-averaged along-flow velocity [m s⁻¹]
  A  = Glen rate factor [Pa⁻³ s⁻¹]
  W  = flow-tube width [m]
  n  = Glen exponent (= 3)

NOTE:
  The erroneous factor-of-2 denominator (A W/2) was excised in Phase 5.2.2.5.
  The correct formula has denominator (A W) only, as confirmed by derivation.

The lateral stress is then converted to a depth-integrated body force per
unit plan area by integrating over the two vertical sidewalls:
  F_lateral = 2 · τ_wall · H · Δx   [N]
  Area_plan = W · Δx                 [m²]
  τ_lat_i = (2 H_i / W_i) · τ_wall_i [Pa]

In the depth-integrated 1-D SSA momentum equation (force per unit plan area):
  Lateral resistive stress contribution = (2 H / W) · τ_wall   [Pa]

(Both lateral walls contribute; factor 2 appears here, scaled by aspect ratio H/W.)

Units:  SI.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import CONST, PhysicsConstants


class LateralDrag:
    """
    Lateral drag (rock-wall shear) for narrow-fjord flowlines.

    Parameters
    ----------
    const : PhysicsConstants
    A : float, optional
        Glen rate factor override [Pa⁻³ s⁻¹].
    """

    def __init__(
        self,
        const: PhysicsConstants = CONST,
        A: float | None = None,
    ) -> None:
        self.const = const
        self.n: float = const.glen_n
        self.A: float = A if A is not None else const.A_default
        self.shape_factor: float = const.lateral_shape_factor  # = 5

    # ------------------------------------------------------------------
    # Wall shear stress
    # ------------------------------------------------------------------

    def tau_wall(
        self, u: NDArray[np.float64], width: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """
        Lateral wall shear stress τ_wall [Pa].

        τ_wall_i = (5 |u_i| / (A W_i))^(1/n)

        The absolute value of u is used because wall shear opposes flow
        regardless of direction.

        Parameters
        ----------
        u : ndarray [m s⁻¹], shape (N,)
        width : ndarray [m], shape (N,)

        Returns
        -------
        tau_w : ndarray [Pa], shape (N,)
        """
        u = np.asarray(u, dtype=np.float64)
        width = np.asarray(width, dtype=np.float64)
        arg = self.shape_factor * np.abs(u) / (self.A * width)
        # arg has units of Pa^n (resolved by the 1/n power) → Pa
        return arg ** (1.0 / self.n)

    def lateral_body_force(
        self,
        u: NDArray[np.float64],
        width: NDArray[np.float64],
        H: NDArray[np.float64] | float = 1.0,
    ) -> NDArray[np.float64]:
        """
        Lateral drag body force per unit plan-area [Pa].

        In the depth-integrated 1-D SSA:
          Lateral resistive stress = (2 H / W) · τ_wall   [Pa]

        (Two walls; sidewall area = 2 H Δx, plan area = W Δx;
        effective resisting stress per unit plan area = (2 H / W) τ_wall.)

        Parameters
        ----------
        u : ndarray [m s⁻¹], shape (N,)
        width : ndarray [m], shape (N,)
        H : ndarray [m], shape (N,) or float, default 1.0

        Returns
        -------
        f_lat : ndarray [Pa], shape (N,)
            Signed: positive acts in -x direction (resists positive flow).
        """
        u = np.asarray(u, dtype=np.float64)
        width = np.asarray(width, dtype=np.float64)
        H_arr = np.asarray(H, dtype=np.float64)
        tw = self.tau_wall(u, width)
        # Signed: lateral drag opposes the sign of u
        sign_u = np.where(u >= 0.0, 1.0, -1.0)
        return sign_u * 2.0 * H_arr * tw / width

    def beta_lateral(
        self,
        u: NDArray[np.float64],
        width: NDArray[np.float64],
        H: NDArray[np.float64] | float = 1.0,
    ) -> NDArray[np.float64]:
        """
        Linearised lateral drag coefficient β_lat [Pa s m⁻¹] for Picard.

        τ_lat ≈ β_lat · u  →  β_lat = |τ_lat| / |u|  (for u ≠ 0)
        At u = 0: β_lat = 0 (no lateral drag without flow).

        β_lat_i = (2 H_i / W_i) · τ_wall_i / |u_i|   for |u_i| > u_scale
        β_lat_i = 0                                   for |u_i| ≤ u_scale

        Parameters
        ----------
        u : ndarray [m s⁻¹], shape (N,)
        width : ndarray [m], shape (N,)
        H : ndarray [m], shape (N,) or float, default 1.0
        """
        u = np.asarray(u, dtype=np.float64)
        u_scale = self.const.u_scale  # 10 m/yr in m/s
        f_lat = self.lateral_body_force(u, width, H)
        beta = np.where(np.abs(u) > u_scale, np.abs(f_lat) / np.maximum(np.abs(u), u_scale), 0.0)
        return beta

    def __repr__(self) -> str:
        return (
            f"LateralDrag(n={self.n}, A={self.A:.2e}, "
            f"shape_factor={self.shape_factor})"
        )

