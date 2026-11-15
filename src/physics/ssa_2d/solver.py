"""
src/physics/ssa_2d/solver.py
============================
Non-linear Picard momentum solver for 2D Shallow Shelf Approximation (SSA).

Solves the non-linear coupled elliptic boundary value problem:
  - div(T) + beta_b(u, v) * u = - rho_i * g * H * grad(s)

Features:
  - Picard fixed-point iteration with under-relaxation (omega in [0.4, 0.8]).
  - Rigorous dual convergence criteria:
      1. Relative non-linear momentum residual ||R||_2 / ||R_0||_2 < tol_rel (default 1e-5).
      2. Infinity norm of velocity update ||Delta u||_inf < tol_vel (default 0.1 m/yr).
  - Explicit convergence diagnostics and iteration history logging.
  - Fail-safe rollback and exception raising on iteration limit or numerical breakdown.
"""

from __future__ import annotations
import dataclasses
import time
import warnings
import numpy as np
from numpy.typing import NDArray
import scipy.sparse.linalg as spla

from .constants import SSA2DConstants, CONST_DEFAULT
from .grid import Grid2D
from .rheology import compute_effective_viscosity_2d
from .friction import compute_flotation_fraction_and_surface, compute_basal_drag_coefficient
from .assembly import assemble_ssa_system_2d


class NonlinearConvergenceError(RuntimeError):
    """Raised when the 2D SSA non-linear Picard solver fails to converge."""
    pass


@dataclasses.dataclass
class SSAResult2D:
    """Container for 2D SSA solver output and convergence diagnostics."""
    u: NDArray[np.float64]              # Horizontal along-flow velocity [m s⁻¹] (Ny, Nx)
    v: NDArray[np.float64]              # Horizontal across-flow velocity [m s⁻¹] (Ny, Nx)
    nu: NDArray[np.float64]             # Depth-averaged effective viscosity [Pa s] (Ny, Nx)
    beta_b: NDArray[np.float64]         # Basal drag coefficient [Pa s m⁻¹] (Ny, Nx)
    f_gr: NDArray[np.float64]           # Sub-grid grounded fraction in [0, 1] (Ny, Nx)
    s: NDArray[np.float64]              # Surface elevation [m] (Ny, Nx)
    n_iter: int                         # Number of Picard iterations taken
    final_residual: float               # Final relative L2 residual
    final_vel_step: float               # Final velocity update norm [m yr⁻¹]
    converged: bool                     # True if both convergence criteria were satisfied
    solve_time_sec: float               # Wall-clock execution time [s]
    history: list[dict[str, float]]     # Per-iteration metrics


class SSASolver2D:
    """
    2D Depth-Integrated SSA Momentum Solver.
    """

    def __init__(
        self,
        const: SSA2DConstants = CONST_DEFAULT,
        omega: float | None = None,
        max_iter: int | None = None,
        tol_rel_residual: float | None = None,
        tol_vel_step: float | None = None,
    ) -> None:
        self.const = const
        self.omega = omega if omega is not None else const.picard_omega
        self.max_iter = max_iter if max_iter is not None else const.picard_max_iter
        self.tol_rel = tol_rel_residual if tol_rel_residual is not None else const.tol_rel_residual
        self.tol_vel = tol_vel_step if tol_vel_step is not None else const.tol_vel_step

    def solve(
        self,
        grid: Grid2D,
        H: NDArray[np.float64],
        b: NDArray[np.float64],
        s: NDArray[np.float64] | None = None,
        u_init: NDArray[np.float64] | None = None,
        v_init: NDArray[np.float64] | None = None,
        C_bed: float | NDArray[np.float64] | None = None,
        u_dirichlet: NDArray[np.float64] | None = None,
        v_dirichlet: NDArray[np.float64] | None = None,
        raise_on_failure: bool = True,
    ) -> SSAResult2D:
        """
        Solve 2D SSA momentum balance on the given grid and geometry.

        Parameters
        ----------
        grid : Grid2D
        H : NDArray[np.float64]
            Ice thickness [m] (Ny, Nx).
        b : NDArray[np.float64]
            Bedrock elevation [m] (Ny, Nx).
        s : NDArray[np.float64] | None
            Surface elevation [m]. If None, computed from flotation.
        u_init : NDArray[np.float64] | None
            Initial guess for u [m s⁻¹].
        v_init : NDArray[np.float64] | None
            Initial guess for v [m s⁻¹].
        C_bed : float | NDArray[np.float64] | None
            Basal drag parameter. If None, uses const.C_bed.
        u_dirichlet : NDArray[np.float64] | None
        v_dirichlet : NDArray[np.float64] | None
        raise_on_failure : bool
            If True, raises NonlinearConvergenceError upon failure.

        Returns
        -------
        SSAResult2D
        """
        t0 = time.perf_counter()
        Nx, Ny = grid.Nx, grid.Ny
        spy = self.const.sec_per_year
        C_b = C_bed if C_bed is not None else self.const.C_bed

        # Flotation and surface elevation
        f_gr_diag, s_diag, _ = compute_flotation_fraction_and_surface(H, b, self.const)
        s_eval = s if s is not None else s_diag
        f_gr = f_gr_diag

        # Velocity initialization
        if u_init is not None:
            u = u_init.copy().astype(np.float64)
        else:
            u = np.zeros((Ny, Nx), dtype=np.float64)

        if v_init is not None:
            v = v_init.copy().astype(np.float64)
        else:
            v = np.zeros((Ny, Nx), dtype=np.float64)

        # Enforce kinematic boundaries on initial guess
        if grid.bc_west in ("divide", "free_slip"):
            u[:, 0] = 0.0
        if grid.bc_south in ("free_slip", "symmetry"):
            v[0, :] = 0.0
        elif grid.bc_south == "no_slip":
            u[0, :] = 0.0
            v[0, :] = 0.0
        if grid.bc_north in ("free_slip", "symmetry"):
            v[-1, :] = 0.0
        elif grid.bc_north == "no_slip":
            u[-1, :] = 0.0
            v[-1, :] = 0.0

        history: list[dict[str, float]] = []
        converged = False
        res_0 = None
        final_rel_res = 1.0
        final_step = 1.0

        nu = compute_effective_viscosity_2d(u, v, grid, self.const)
        beta_b = compute_basal_drag_coefficient(u, v, f_gr, C_b, self.const)

        for it in range(self.max_iter):
            # 1. Update coefficients from previous iterate
            nu = compute_effective_viscosity_2d(u, v, grid, self.const)
            beta_b = compute_basal_drag_coefficient(u, v, f_gr, C_b, self.const)

            # 2. Assemble sparse linear system
            A, rhs = assemble_ssa_system_2d(
                grid=grid,
                H=H,
                s=s_eval,
                b=b,
                nu=nu,
                beta_b=beta_b,
                const=self.const,
                u_dirichlet=u_dirichlet,
                v_dirichlet=v_dirichlet,
            )

            # Initial residual for scaling
            w_current = np.concatenate([u.ravel(), v.ravel()])
            cur_res_vec = A @ w_current - rhs
            cur_res_norm = float(np.linalg.norm(cur_res_vec))

            if it == 0:
                res_0 = max(cur_res_norm, 1.0e-12)

            rel_res = cur_res_norm / res_0
            final_rel_res = rel_res

            # 3. Direct sparse linear solve
            try:
                sol = spla.spsolve(A, rhs)
            except Exception as e:
                if raise_on_failure:
                    raise NonlinearConvergenceError(f"Linear solver failed at Picard iteration {it+1}: {e}") from e
                warnings.warn(f"Linear solver failure: {e}", stacklevel=2)
                break

            if np.any(np.isnan(sol)) or np.any(np.isinf(sol)):
                if raise_on_failure:
                    raise NonlinearConvergenceError(f"NaN or Inf encountered in solution at iteration {it+1}")
                warnings.warn(f"NaN/Inf in solution at iteration {it+1}", stacklevel=2)
                break

            u_cand = sol[:grid.total_cells].reshape((Ny, Nx))
            v_cand = sol[grid.total_cells:].reshape((Ny, Nx))

            # 4. Check step change
            du_inf = float(np.max(np.abs(u_cand - u)))
            dv_inf = float(np.max(np.abs(v_cand - v)))
            step_inf = max(du_inf, dv_inf)
            step_inf_ann = step_inf * spy
            final_step = step_inf_ann

            # 5. Under-relaxation update
            omega = self.omega
            u_next = omega * u_cand + (1.0 - omega) * u
            v_next = omega * v_cand + (1.0 - omega) * v

            history.append({
                "iteration": it + 1,
                "rel_residual": rel_res,
                "step_inf_m_yr": step_inf_ann,
                "max_u_m_yr": float(np.max(np.abs(u_next))) * spy,
                "max_v_m_yr": float(np.max(np.abs(v_next))) * spy,
            })

            # Check convergence (skip it=0 to allow initial development)
            if it >= 1 and rel_res < self.tol_rel and step_inf < self.tol_vel:
                converged = True
                u = u_next
                v = v_next
                break

            u = u_next
            v = v_next

        solve_time = time.perf_counter() - t0

        if not converged and raise_on_failure:
            raise NonlinearConvergenceError(
                f"2D SSA Picard solver reached iteration limit {self.max_iter} without converging. "
                f"Final rel_residual={final_rel_res:.4e} (tol={self.tol_rel}), "
                f"step_inf={final_step:.4e} m/yr (tol={self.tol_vel * spy:.4e} m/yr)."
            )

        return SSAResult2D(
            u=u,
            v=v,
            nu=nu,
            beta_b=beta_b,
            f_gr=f_gr,
            s=s_eval,
            n_iter=len(history),
            final_residual=final_rel_res,
            final_vel_step=final_step,
            converged=converged,
            solve_time_sec=solve_time,
            history=history,
        )

