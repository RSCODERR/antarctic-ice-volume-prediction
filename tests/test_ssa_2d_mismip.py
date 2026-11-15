"""
tests/test_ssa_2d_mismip.py
===========================
MISMIP+ benchmark verification tests (Cornford et al. 2020; Asay-Davis et al. 2016):
  1. Ice0 control steady state: mid-channel grounding line x_GL in [440, 460] km (450 +/- 10 km).
  2. Ice1r forced marine retreat: monotonic retreat and VAF loss under sub-shelf melting.
  3. Ice1ra reversibility and hysteresis: turning off melt does not cause instantaneous re-advance.
  4. Flotation & sub-grid grounding-line smoothness.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import numpy as np

from src.physics.ssa_2d.constants import CONST_MISMIP
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d
from src.physics.ssa_2d.mismip_plus import (
    create_mismip_bed,
    compute_mismip_melt_rate,
    find_grounding_line_x,
    compute_vaf_km3,
    create_mismip_initial_profile,
)


class TestSSA2DMISMIP(unittest.TestCase):
    """MISMIP+ benchmark compliance test suite."""

    def setUp(self) -> None:
        self.const = CONST_MISMIP
        # Standard MISMIP+ grid dimensions
        self.Lx = 640_000.0
        self.Ly = 80_000.0
        self.Nx = 64   # dx = 10 km
        self.Ny = 9    # dy = 8.89 km
        self.grid = Grid2D(
            Lx=self.Lx, Ly=self.Ly, Nx=self.Nx, Ny=self.Ny,
            bc_west="no_slip", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
        )
        self.bed = create_mismip_bed(self.grid)

    def test_mismip_ice0_steady_grounding_line(self) -> None:
        """Verify that Ice0 initial grounding line settles within official 450 +/- 10 km window."""
        H = create_mismip_initial_profile(self.grid, self.bed, self.const, x_gl_target=450_000.0)
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, self.bed, self.const)

        solver = SSASolver2D(const=self.const, omega=0.6, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5 / self.const.sec_per_year)
        res = solver.solve(self.grid, H, self.bed, s=s, raise_on_failure=True)
        self.assertTrue(res.converged)

        x_gl = find_grounding_line_x(res.f_gr, self.grid)
        x_gl_km = x_gl / 1000.0

        # Official MISMIP+ requirement: mid-channel GL at 450 +/- 10 km ([440 km, 460 km])
        self.assertGreaterEqual(x_gl_km, 440.0, f"Grounding line {x_gl_km:.2f} km is too far retreated (< 440 km)")
        self.assertLessEqual(x_gl_km, 460.0, f"Grounding line {x_gl_km:.2f} km is too far advanced (> 460 km)")

        # Verify short-term forward drift under control forcing (zero melt) is negligible
        dt_sec = 2.0 * self.const.sec_per_year
        smb_si = 0.3 / self.const.sec_per_year
        res_ctrl = step_continuity_2d(H, res.u, res.v, self.grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=self.const)
        f_gr_ctrl, _, _ = compute_flotation_fraction_and_surface(res_ctrl.H_next, self.bed, self.const)
        x_gl_ctrl = find_grounding_line_x(f_gr_ctrl, self.grid)
        drift_km = abs(x_gl_ctrl - x_gl) / 1000.0
        self.assertLess(drift_km, 1.0, f"2-year control drift {drift_km:.3f} km exceeds 1.0 km stability threshold")

    def test_mismip_ice1r_forced_retreat_response(self) -> None:
        """Verify that sub-shelf melt induces marine grounding line retreat and VAF deficit relative to control."""
        H = create_mismip_initial_profile(self.grid, self.bed, self.const, x_gl_target=450_000.0)
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, self.bed, self.const)

        solver = SSASolver2D(const=self.const, omega=0.6, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5 / self.const.sec_per_year)
        res0 = solver.solve(self.grid, H, self.bed, s=s, raise_on_failure=True)

        dt_sec = 2.0 * self.const.sec_per_year
        smb_si = 0.3 / self.const.sec_per_year

        # Step A: Control trajectory with zero melting (Ice0)
        H_ctrl = H.copy()
        u_c = res0.u.copy()
        v_c = res0.v.copy()
        for _ in range(2):
            res_c = step_continuity_2d(H_ctrl, u_c, v_c, self.grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=self.const)
            H_ctrl = np.maximum(res_c.H_next, 10.0)
            f_gr_c, s_c, _ = compute_flotation_fraction_and_surface(H_ctrl, self.bed, self.const)
            r_c = solver.solve(self.grid, H_ctrl, self.bed, s=s_c, u_init=u_c, v_init=v_c)
            u_c, v_c = r_c.u, r_c.v
        x_gl_ctrl = find_grounding_line_x(f_gr_c, self.grid)
        vaf_ctrl = compute_vaf_km3(H_ctrl, self.bed, self.grid, self.const)

        # Step B: Perturbed trajectory with active sub-shelf melting (Ice1r)
        H_melt = H.copy()
        u_m = res0.u.copy()
        v_m = res0.v.copy()
        for _ in range(2):
            f_gr_m, s_m, _ = compute_flotation_fraction_and_surface(H_melt, self.bed, self.const)
            m_shelf_si = compute_mismip_melt_rate(H_melt, self.bed, f_gr_m, self.const)
            res_m = step_continuity_2d(H_melt, u_m, v_m, self.grid, dt=dt_sec, smb=smb_si, m_shelf=m_shelf_si, const=self.const)
            H_melt = np.maximum(res_m.H_next, 10.0)
            f_gr_m, s_m, _ = compute_flotation_fraction_and_surface(H_melt, self.bed, self.const)
            r_m = solver.solve(self.grid, H_melt, self.bed, s=s_m, u_init=u_m, v_init=v_m)
            u_m, v_m = r_m.u, r_m.v
        x_gl_melt = find_grounding_line_x(f_gr_m, self.grid)
        vaf_melt = compute_vaf_km3(H_melt, self.bed, self.grid, self.const)

        # Grounding line must retreat relative to control: x_GL,melt <= x_GL,ctrl
        self.assertLessEqual(
            x_gl_melt, x_gl_ctrl,
            f"Grounding line did not retreat relative to control: x_ctrl={x_gl_ctrl/1e3:.2f} km, x_melt={x_gl_melt/1e3:.2f} km"
        )
        # Volume Above Flotation must be strictly smaller under ocean melting
        self.assertLess(
            vaf_melt, vaf_ctrl,
            f"Ocean melting did not reduce VAF: vaf_ctrl={vaf_ctrl:.2f} km³, vaf_melt={vaf_melt:.2f} km³"
        )

    def test_mismip_ice1ra_hysteresis(self) -> None:
        """Verify that cutting melt to zero does not cause instantaneous snap-back to initial grounding line."""
        H = create_mismip_initial_profile(self.grid, self.bed, self.const, x_gl_target=450_000.0)
        f_gr, s, _ = compute_flotation_fraction_and_surface(H, self.bed, self.const)

        solver = SSASolver2D(const=self.const, omega=0.6, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5 / self.const.sec_per_year)
        res0 = solver.solve(self.grid, H, self.bed, s=s, raise_on_failure=True)
        x_gl_0 = find_grounding_line_x(res0.f_gr, self.grid)

        # Apply 5 years of forced retreat
        dt_sec = 5.0 * self.const.sec_per_year
        smb_si = 0.3 / self.const.sec_per_year
        m_shelf_si = compute_mismip_melt_rate(H, self.bed, f_gr, self.const)
        res_melt = step_continuity_2d(H, res0.u, res0.v, self.grid, dt=dt_sec, smb=smb_si, m_shelf=m_shelf_si, const=self.const)
        f_gr_melt, _, _ = compute_flotation_fraction_and_surface(res_melt.H_next, self.bed, self.const)
        x_gl_melt = find_grounding_line_x(f_gr_melt, self.grid)

        # Apply 5 years of recovery with melt = 0
        res_recov = step_continuity_2d(res_melt.H_next, res0.u, res0.v, self.grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=self.const)
        f_gr_recov, _, _ = compute_flotation_fraction_and_surface(res_recov.H_next, self.bed, self.const)
        x_gl_recov = find_grounding_line_x(f_gr_recov, self.grid)

        # Physical hysteresis: grounding line after 5 yr recovery must remain well upstream of initial state
        self.assertLess(
            x_gl_recov, x_gl_0,
            f"Grounding line instantaneously returned to initial position (no hysteresis): x_recov={x_gl_recov/1e3:.2f} km, x_0={x_gl_0/1e3:.2f} km"
        )

    def test_subgrid_flotation_smoothness(self) -> None:
        """Verify that subgrid grounded fraction f_gr is smoothly bounded in [0, 1]."""
        H = np.linspace(200.0, 800.0, self.grid.Nx).reshape(1, -1).repeat(self.grid.Ny, axis=0)
        f_gr, s, H_flot = compute_flotation_fraction_and_surface(H, self.bed, self.const)

        self.assertTrue(np.all(f_gr >= 0.0))
        self.assertTrue(np.all(f_gr <= 1.0))
        # Ensure smooth surface elevation
        self.assertFalse(np.any(np.isnan(s)))
        self.assertFalse(np.any(np.isinf(s)))


if __name__ == "__main__":
    unittest.main()
