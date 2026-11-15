"""
src/physics/continuity.py
=========================
FVContinuitySolver — Fixed-Grid Eulerian + Flotation Remapping (FGE-FR).

Implements the Phase 5.2.2.7 master discrete state-update algorithm exactly
as specified (Steps 1–11), including:

  - Eulerian FV transport (Steps 5a–5d)
  - Flotation remapping via height-above-buoyancy (Steps 7a–7b)
  - Retreat bookkeeping (Steps 9a–9b)
  - Advance bookkeeping (Steps 9c)
  - CFL-type timestep check (Section 2.5)
  - Diagnostic conservation residual (Step 11)
  - Bilateral ledger conservation check

Units:  SI throughout.
"""

from __future__ import annotations
import dataclasses
import warnings
import numpy as np
from numpy.typing import NDArray

from .constants import CONST, PhysicsConstants
from .state import IceState
from .ssa_solver import SSASolver, SSAResult
from .grounding_line import SchoofGLFlux
from .smb import SMBConverter


class ConservationError(RuntimeError):
    """Raised when the discrete mass budget does not close."""


class CFLViolation(RuntimeError):
    """Raised when the grounding line moves more than one full cell per step."""


@dataclasses.dataclass
class StepDiagnostics:
    """Diagnostic output from one FGE-FR timestep."""
    t_start: float          # [s]
    t_end: float            # [s]
    dt: float               # [s]
    M_gr_start: float       # [kg]
    M_gr_end: float         # [kg]
    floating_start: float   # [kg]
    floating_end: float     # [kg]
    Mdot_SMB: float         # [kg s⁻¹]
    Q_GL: float             # [m³ s⁻¹]
    v_GL: float             # [m s⁻¹]
    dM_boundary: float      # [kg]
    residual: float         # [kg]
    gl_cell_start: int
    gl_cell_end: int
    gl_frac_start: float
    gl_frac_end: float
    ssa_converged: bool
    ssa_n_iter: int
    ssa_picard_residual: float
    cfl_ok: bool
    event: str
    u: NDArray[np.float64] | None = None


class FVContinuitySolver:
    """
    One-step FGE-FR integrator for a 1-D Peninsula flowline.

    Parameters
    ----------
    const : PhysicsConstants
    ssa : SSASolver
    gl_flux : SchoofGLFlux
    smb_conv : SMBConverter
    conservation_tol_rel : float
        Relative tolerance for the Step 11 residual check. Default 1e-10.
    use_schoof : bool
        Use Schoof GL flux. Set False for land-terminating flowlines.
    """

    def __init__(
        self,
        const: PhysicsConstants = CONST,
        ssa: SSASolver | None = None,
        gl_flux: SchoofGLFlux | None = None,
        smb_conv: SMBConverter | None = None,
        conservation_tol_rel: float = 1e-10,
        use_schoof: bool = True,
    ) -> None:
        self.const = const
        self.ssa = ssa if ssa is not None else SSASolver(const)
        self.gl_flux = gl_flux if gl_flux is not None else SchoofGLFlux(const)
        self.smb_conv = smb_conv if smb_conv is not None else SMBConverter(const)
        self.conservation_tol_rel = conservation_tol_rel
        self.use_schoof = use_schoof

    def step(
        self,
        state: IceState,
        smb_m_s: NDArray[np.float64],
        dt: float,
        u_init: NDArray[np.float64] | None = None,
        u_upstream: float | None = None,
        use_lateral: bool = True,
    ) -> tuple[IceState, StepDiagnostics]:
        # --- STEP 1: State load ---
        state.assert_gl_valid()
        state.assert_no_negative_thickness()

        g_n = state.gl_cell
        lam_n = state.gl_frac
        t_n = state.t
        M_gr_n = state.compute_grounded_mass_kg()
        floating_n = state.floating_mass_kg

        dx = state.dx
        N = state.N
        N_gr = g_n + 1

        # --- STEP 2–3: SSA diagnostic solve ---
        ssa_result = self.ssa.solve(
            state, u_init=u_init, u_upstream=u_upstream, use_lateral=use_lateral
        )
        u = ssa_result.u

        # --- STEP 4: Schoof or kinematic GL flux ---
        H_GL = state.H_gl
        W_GL = state.W_gl

        if self.use_schoof:
            Q_GL = self.gl_flux.Q_gl(H_GL, W_GL)
        else:
            u_GL = float(u[g_n]) if not np.isnan(u[g_n]) else 0.0
            Q_GL = self.gl_flux.Q_kinematic(H_GL, W_GL, u_GL)

        # --- STEP 5a: Face fluxes ---
        Q_faces = self.ssa.face_fluxes(state, u)

        # --- STEP 5b–5d: Eulerian FV transport (intermediate state H*) ---
        H_star = state.H.copy()
        S = self.smb_conv.cell_volume_source(smb_m_s, state.width, dx)

        # Interior cells i = 0 … g_n - 1 (fully grounded)
        for i in range(N_gr - 1):
            cell_vol = state.width[i] * dx
            q_in = Q_faces[i - 1] if i > 0 else 0.0
            q_out = Q_faces[i]
            H_star[i] += dt / cell_vol * (q_in - q_out + S[i])

        # Terminal partial cell i = g_n: scaled by partial-cell fraction
        g = g_n
        effective_vol = state.width[g] * lam_n * dx
        q_in_g = Q_faces[g - 1] if g > 0 else 0.0
        S_term_grounded = S[g] * lam_n
        H_star[g] += dt / effective_vol * (q_in_g - Q_GL + S_term_grounded)

        # --- STEP 6: SMB mass accumulator (diagnostic) ---
        Mdot_SMB = float(
            np.sum(S[:g]) * self.const.rho_ice + S_term_grounded * self.const.rho_ice
        )

        # Mass of intermediate field H* on the OLD grounded domain:
        M_star_old_gr = float(
            np.sum(state.width[:g_n] * H_star[:g_n]) * dx * self.const.rho_ice
            + state.width[g_n] * lam_n * dx * H_star[g_n] * self.const.rho_ice
        )

        # --- STEP 7: Flotation remapping via Height Above Buoyancy ---
        H_crit = (self.const.rho_water / self.const.rho_ice) * np.maximum(
            0.0, state.sea_level - state.bed
        )
        hab = H_star - H_crit

        grounded_indices = np.where(hab >= 0.0)[0]
        if len(grounded_indices) == 0:
            raise ConservationError(
                "All cells became floating after one timestep. Catastrophic ungrounding."
            )

        g_new = int(grounded_indices[-1])

        # Sub-cell GL fraction interpolation using continuous height above buoyancy
        if g_new + 1 < N:
            hab_g = hab[g_new]
            hab_next = hab[g_new + 1]
            denom = hab_g - hab_next
            if abs(denom) > 1e-6:
                # Fractional position of zero-crossing; regularized floor at 0.05
                lam_new = float(np.clip(hab_g / denom, 0.05, 1.0))
            else:
                lam_new = 1.0
        else:
            lam_new = 1.0

        # --- STEP 8: Boundary migration velocity and exact discrete mass term ---
        x_GL_n = state.x_gl
        x_GL_new = (state.x_centres[g_new] - 0.5 * dx) + lam_new * dx
        v_GL = (x_GL_new - x_GL_n) / dt

        # CFL check
        cfl_ok = abs(g_new - g_n) <= 1
        if not cfl_ok:
            raise CFLViolation(
                f"CFL violated: GL moved {abs(g_new - g_n)} cells in one step "
                f"(v_GL = {v_GL * self.const.yr_to_s:.1f} m/yr). "
                f"Halve Δt. RSK_NUM_08 triggered."
            )

        # Compute grounded mass on NEW domain:
        M_gr_new = float(
            np.sum(state.width[:g_new] * H_star[:g_new]) * dx * self.const.rho_ice
            + state.width[g_new] * lam_new * dx * H_star[g_new] * self.const.rho_ice
        )

        # Exact discrete Reynolds boundary mass transfer:
        dM_boundary = M_gr_new - M_star_old_gr

        # --- STEPS 9: Retreat or advance bilateral bookkeeping ---
        floating_new = floating_n - dM_boundary
        if floating_new < -1e-6 * M_gr_n:
            raise ConservationError(
                f"Floating reservoir went negative ({floating_new:.4e} kg). "
                "Advance bookkeeping error."
            )

        if g_new < g_n:
            event = "full_unground"
        elif g_new > g_n:
            event = "full_ground"
        elif lam_new < lam_n:
            event = "partial_retreat"
        elif lam_new > lam_n:
            event = "partial_advance"
        else:
            event = "stable"

        # --- STEP 10: Final state creation ---
        new_H = H_star.copy()
        if np.any(new_H < -1e-3):
            raise ConservationError(
                "Negative ice thickness > 1 mm in Eulerian transport step. "
                "Check SMB forcing or timestep size."
            )
        new_H = np.maximum(new_H, 0.0)

        new_state = IceState(
            H=new_H,
            bed=state.bed.copy(),
            width=state.width.copy(),
            x_centres=state.x_centres.copy(),
            gl_cell=g_new,
            gl_frac=lam_new,
            t=t_n + dt,
            floating_mass_kg=floating_new,
            sea_level=state.sea_level,
        )

        # --- STEP 11: Diagnostic conservation residual ---
        residual = (
            M_gr_new
            - M_gr_n
            - dt * Mdot_SMB
            + dt * self.const.rho_ice * Q_GL
            - dM_boundary
        )

        tol = self.conservation_tol_rel * max(abs(M_gr_n), 1.0)
        if abs(residual) > tol:
            raise ConservationError(
                f"Mass budget does not close at t={t_n * self.const.s_to_yr:.4f} yr. "
                f"Residual = {residual:.6e} kg (tol = {tol:.6e} kg). "
                f"ΔM_gr = {M_gr_new - M_gr_n:.6e} kg. "
                f"dt·Mdot_SMB = {dt * Mdot_SMB:.6e} kg. "
                f"dt·ρ_i·Q_GL = {dt * self.const.rho_ice * Q_GL:.6e} kg. "
                f"ΔM_boundary = {dM_boundary:.6e} kg."
            )

        diag = StepDiagnostics(
            t_start=t_n,
            t_end=t_n + dt,
            dt=dt,
            M_gr_start=M_gr_n,
            M_gr_end=M_gr_new,
            floating_start=floating_n,
            floating_end=floating_new,
            Mdot_SMB=Mdot_SMB,
            Q_GL=Q_GL,
            v_GL=v_GL,
            dM_boundary=dM_boundary,
            residual=residual,
            gl_cell_start=g_n,
            gl_cell_end=g_new,
            gl_frac_start=lam_n,
            gl_frac_end=lam_new,
            ssa_converged=ssa_result.converged,
            ssa_n_iter=ssa_result.n_iter,
            ssa_picard_residual=ssa_result.residual,
            cfl_ok=cfl_ok,
            event=event,
            u=u.copy(),
        )

        return new_state, diag

    def run(
        self,
        state: IceState,
        smb_m_s: NDArray[np.float64],
        n_steps: int,
        dt: float | None = None,
        verbose: bool = False,
    ) -> tuple[list[IceState], list[StepDiagnostics]]:
        if dt is None:
            dt = self.const.dt_target

        states = [state]
        diags: list[StepDiagnostics] = []
        u_prev = None

        for step_idx in range(n_steps):
            s = states[-1]
            try:
                s_new, d = self.step(s, smb_m_s, dt, u_init=u_prev)
            except (ConservationError, CFLViolation) as e:
                raise type(e)(
                    f"[step {step_idx}, t={s.t * self.const.s_to_yr:.4f} yr] {e}"
                ) from e

            u_prev = d.u
            states.append(s_new)
            diags.append(d)

            if verbose:
                yr = s_new.t * self.const.s_to_yr
                print(
                    f" step {step_idx + 1:4d}: t={yr:8.3f} yr "
                    f"M_gr={d.M_gr_end * self.const.kg_to_Gt:.6f} Gt "
                    f"x_GL={s_new.x_gl / 1e3:.3f} km "
                    f"event={d.event:16s} "
                    f"res={d.residual:.2e} kg "
                    f"SSA_conv={d.ssa_converged}"
                )

        return states, diags

    def __repr__(self) -> str:
        return (
            f"FVContinuitySolver(use_schoof={self.use_schoof}, "
            f"conservation_tol_rel={self.conservation_tol_rel:.1e})"
        )
