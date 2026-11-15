"""
src/physics/ssa_solver.py
=========================
SSASolver — Picard-linearised 1-D Shallow-Shelf Approximation (SSA) solver.

Solves the 1-D depth-integrated SSA momentum equation:

  d/dx [2 H ν_eff du/dx] − β_b(u) · u − β_lat(u) · u = ρ_i g H ds/dx

where s = H + z_b is the ice surface elevation.

Discretisation:
  - Second-order finite-difference on the FIXED grid (cell-centred velocities).
  - Picard linearisation: at each iteration, ν_eff and β are evaluated at u^(k)
    and held fixed to form a tridiagonal linear system for u^(k+1).
  - Under-relaxation: u^(k+1) ← ω u^(k+1) + (1-ω) u^(k), ω ∈ [0.4, 0.6].

Boundary conditions:
  - Upstream (i=0): Neumann (zero-stress, du/dx = 0) or prescribed velocity.
  - Downstream (i=g): Stress-free calving front.

Convergence:
  Res_Picard = ||u^(k+1) − u^(k)|| / (||u^(k)|| + u_scale · √N) ≤ 1×10⁻⁵
  Engineering limit: up to 40 iterations.

Units:  SI throughout.
"""

from __future__ import annotations
import dataclasses
import warnings
import numpy as np
from numpy.typing import NDArray
from scipy import linalg

from .constants import CONST, PhysicsConstants
from .rheology import GlensFlowLaw
from .basal_drag import BasalDrag
from .lateral_drag import LateralDrag
from .state import IceState


@dataclasses.dataclass
class SSAResult:
    u: NDArray[np.float64]
    nu_eff: NDArray[np.float64]
    n_iter: int
    residual: float
    converged: bool


class SSASolver:
    """
    Picard-linearised 1-D SSA momentum solver.

    Parameters
    ----------
    const : PhysicsConstants
    rheology : GlensFlowLaw
    basal : BasalDrag
    lateral : LateralDrag
    omega : float
        Under-relaxation parameter ω ∈ [0.4, 0.8]. Default 0.6.
    max_iter : int
        Maximum Picard iterations. Default 40.
    tol : float
        Convergence tolerance on mixed residual. Default 1e-5.
    """

    def __init__(
        self,
        const: PhysicsConstants = CONST,
        rheology: GlensFlowLaw | None = None,
        basal: BasalDrag | None = None,
        lateral: LateralDrag | None = None,
        omega: float | None = None,
        max_iter: int | None = None,
        tol: float | None = None,
    ) -> None:
        self.const = const
        self.rheology = rheology if rheology is not None else GlensFlowLaw(const)
        self.basal = basal if basal is not None else BasalDrag(const)
        self.lateral = lateral if lateral is not None else LateralDrag(const)
        self.omega = omega if omega is not None else 0.6
        self.max_iter = max_iter if max_iter is not None else 40
        self.tol = tol if tol is not None else const.picard_tol
        self.u_scale = const.u_scale

    def solve(
        self,
        state: IceState,
        u_init: NDArray[np.float64] | None = None,
        u_upstream: float | None = None,
        use_lateral: bool = True,
    ) -> SSAResult:
        g = state.gl_cell
        N_gr = g + 1   # number of grounded cells

        H = state.H[:N_gr].copy()
        bed = state.bed[:N_gr].copy()
        width = state.width[:N_gr].copy()
        dx = state.dx

        # Surface slope (s = H + z_b)
        surf = H + bed
        ds_dx = np.zeros(N_gr, dtype=np.float64)
        ds_dx[:-1] = (surf[1:] - surf[:-1]) / dx
        ds_dx[-1] = ds_dx[-2]

        # Initial velocity guess: use provided or estimate from local driving stress
        if u_init is not None:
            u = u_init[:N_gr].copy()
        else:
            # Driving stress: tau_d = rho * g * H * max(0, -ds/dx)
            tau_d = np.maximum(0.0, -ds_dx) * self.const.rho_ice * self.const.g * H
            # Estimate u ~ (tau_d / C_bed)^(1/m)
            u_est = (np.maximum(tau_d, 1.0) / self.basal.C_bed) ** (1.0 / self.basal.m)
            u = np.clip(u_est, 1e-4 / self.const.yr_to_s, 2000.0 / self.const.yr_to_s)

        residual = np.inf
        converged = False

        for k in range(self.max_iter):
            du_dx = self.rheology.strain_rate_from_velocity(u, dx)
            nu_eff = self.rheology.effective_viscosity(du_dx)
            beta_b = self.basal.beta_linearised(u)
            if use_lateral:
                beta_lat = self.lateral.beta_lateral(u, width, H)
            else:
                beta_lat = np.zeros(N_gr, dtype=np.float64)

            u_solve = self._solve_tridiagonal(
                H, nu_eff, beta_b, beta_lat, ds_dx,
                width, dx, N_gr, u_upstream
            )

            u_new = self.omega * u_solve + (1.0 - self.omega) * u

            norm_diff = np.linalg.norm(u_new - u)
            norm_ref = np.linalg.norm(u) + self.u_scale * np.sqrt(N_gr)
            residual = norm_diff / norm_ref

            u = u_new

            if residual <= self.tol:
                converged = True
                break

        if not converged:
            warnings.warn(
                f"SSA Picard did not converge after {self.max_iter} iterations. "
                f"Final residual = {residual:.4e} (tol={self.tol:.1e}). "
                f"RSK_NUM_07 triggered.",
                RuntimeWarning,
                stacklevel=2,
            )

        u_full = np.full(state.N, np.nan, dtype=np.float64)
        nu_full = np.full(state.N, np.nan, dtype=np.float64)
        u_full[:N_gr] = u
        nu_full[:N_gr] = self.rheology.effective_viscosity(
            self.rheology.strain_rate_from_velocity(u, dx)
        )

        return SSAResult(
            u=u_full,
            nu_eff=nu_full,
            n_iter=k + 1,
            residual=float(residual),
            converged=converged,
        )

    def _solve_tridiagonal(
        self,
        H: NDArray[np.float64],
        nu_eff: NDArray[np.float64],
        beta_b: NDArray[np.float64],
        beta_lat: NDArray[np.float64],
        ds_dx: NDArray[np.float64],
        width: NDArray[np.float64],
        dx: float,
        N: int,
        u_upstream: float | None,
    ) -> NDArray[np.float64]:
        rho_i = self.const.rho_ice
        g = self.const.g

        # Face-averaged H and nu
        H_face = 0.5 * (H[:-1] + H[1:])
        nu_face = 0.5 * (nu_eff[:-1] + nu_eff[1:])
        P = 2.0 * H_face * nu_face / (dx ** 2)

        diag = np.zeros(N, dtype=np.float64)
        sub = np.zeros(N - 1, dtype=np.float64)
        sup = np.zeros(N - 1, dtype=np.float64)
        rhs = np.zeros(N, dtype=np.float64)

        # Interior cells: 1 <= i <= N - 2
        for i in range(1, N - 1):
            sub[i - 1] = P[i - 1]
            sup[i] = P[i]
            diag[i] = -(P[i] + P[i - 1] + beta_b[i] + beta_lat[i])
            rhs[i] = rho_i * g * H[i] * ds_dx[i]

        # Upstream BC: i=0
        if u_upstream is not None:
            diag[0] = 1.0
            sup[0] = 0.0
            rhs[0] = u_upstream
        else:
            # Neumann (du/dx = 0 at divide): zero flux through face -1/2
            diag[0] = -(P[0] + beta_b[0] + beta_lat[0])
            sup[0] = P[0]
            rhs[0] = rho_i * g * H[0] * ds_dx[0]

        # Downstream BC: i=N-1 (stress-free calving front)
        diag[N - 1] = -(P[N - 2] + beta_b[N - 1] + beta_lat[N - 1])
        sub[N - 2] = P[N - 2]
        rhs[N - 1] = rho_i * g * H[N - 1] * ds_dx[N - 1]

        # Scipy solve_banded layout: (3, N)
        # row 0: superdiagonal ab[0, 1:] = sup
        # row 1: main diagonal ab[1, :] = diag
        # row 2: subdiagonal ab[2, :-1] = sub
        ab = np.zeros((3, N), dtype=np.float64)
        ab[0, 1:] = sup
        ab[1, :] = diag
        ab[2, :-1] = sub

        try:
            u_new = linalg.solve_banded((1, 1), ab, rhs)
        except linalg.LinAlgError as e:
            raise RuntimeError(
                f"SSA tridiagonal solve failed: {e}. Check geometry."
            ) from e

        return u_new

    def face_fluxes(
        self,
        state: IceState,
        u: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        g = state.gl_cell
        N_gr = g + 1
        H = state.H[:N_gr]
        W = state.width[:N_gr]

        # Harmonic-mean face widths
        W_f = 2.0 * W[:-1] * W[1:] / (W[:-1] + W[1:])

        u_gr = u[:N_gr]
        u_face = 0.5 * (u_gr[:-1] + u_gr[1:])

        # First-order upwind thickness
        H_upwind = np.where(u_face >= 0.0, H[:-1], H[1:])

        Q_faces = W_f * H_upwind * u_face

        Q_full = np.full(state.N - 1, np.nan, dtype=np.float64)
        Q_full[:N_gr - 1] = Q_faces
        return Q_full

    def __repr__(self) -> str:
        return f"SSASolver(ω={self.omega}, k_max={self.max_iter}, tol={self.tol:.1e})"
