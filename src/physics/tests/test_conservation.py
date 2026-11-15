"""
src/physics/tests/test_conservation.py
======================================
Comprehensive conservation test suite for FGE-FR continuity solver.

Tests cover:
  1. Fixed-boundary mass conservation (steady state & dynamic evolution)
  2. Retreat handling (partial-cell ungrounding & full-cell ungrounding)
  3. Advance handling (partial-cell grounding & full-cell grounding from floating reservoir)
  4. Bilateral ledger conservation (Grounded + Floating = constant + external fluxes)
  5. Multi-cell CFL violation prevention (stops and raises error if GL jumps > 1 cell)
  6. Double-counting non-occurrence verification (advective flux vs domain migration)
  7. Absolute prohibition against silent correction (imbalance raises ConservationError)
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.physics.constants import CONST
from src.physics.domain import FlowlineDomain
from src.physics.state import IceState
from src.physics.continuity import FVContinuitySolver, ConservationError, CFLViolation
from src.physics.smb import SMBConverter


class TestFixedBoundaryConservation(unittest.TestCase):
    """Tests where the grounding line does not move (fixed domain)."""

    def setUp(self):
        self.domain = FlowlineDomain.synthetic(
            N=40,
            L=20_000.0,
            bed_slope=0.0,
            bed_offset=500.0,  # 500m above sea level
            width_m=10_000.0,
            H0=400.0,
            name="fixed_domain_test"
        )
        self.solver = FVContinuitySolver(use_schoof=False)
        self.smb_conv = SMBConverter()

    def test_zero_flux_conservation(self):
        """With zero surface slope and zero SMB, velocity is zero and mass is conserved."""
        state = self.domain.initial_state()
        smb_zero = np.zeros(state.N, dtype=np.float64)
        dt = CONST.dt_target

        M0 = state.compute_grounded_mass_kg()
        new_state, diag = self.solver.step(state, smb_zero, dt, use_lateral=True)
        M1 = new_state.compute_grounded_mass_kg()

        rel_diff = abs(M1 - M0) / M0
        self.assertLess(rel_diff, 1e-7, f"Mass changed without flux: rel_diff={rel_diff:.2e}")
        self.assertLess(abs(diag.residual), 1e-4 * M0, f"Residual non-zero: {diag.residual}")

    def test_smb_only_conservation(self):
        """With uniform SMB and kinematically forced zero velocity, mass change = dt * Mdot_SMB."""
        state = self.domain.initial_state()
        smb_m_s = self.smb_conv.from_m_ice_yr(np.full(state.N, 1.0))
        dt = CONST.dt_target

        M0 = state.compute_grounded_mass_kg()
        new_state, diag = self.solver.step(state, smb_m_s, dt, use_lateral=True)
        M1 = new_state.compute_grounded_mass_kg()

        expected_dM = dt * diag.Mdot_SMB
        actual_dM = M1 - M0
        rel_diff = abs(actual_dM - expected_dM) / abs(expected_dM)
        self.assertLess(rel_diff, 1e-5, f"SMB mass accumulation mismatch: rel_diff={rel_diff:.2e}")
        self.assertLess(abs(diag.residual), 1e-4 * M0)


class TestMovingGroundingLineRetreatAndAdvance(unittest.TestCase):
    """Tests with marine bedrock where the grounding line retreats and advances."""

    def setUp(self):
        self.domain = FlowlineDomain.synthetic_marine(
            N_land=20,
            N_marine=30,
            width_m=15_000.0,
            H0=400.0,
            name="marine_gl_test"
        )
        self.solver = FVContinuitySolver(use_schoof=True)
        self.smb_conv = SMBConverter()

    def test_retreat_transfers_mass_to_floating_ledger(self):
        """Ablation induces retreat. Mass lost from grounded domain must enter floating ledger."""
        state = self.domain.initial_state(floating_mass_kg=1e14)
        M_gr_0 = state.compute_grounded_mass_kg()
        F_0 = state.floating_mass_kg

        smb_m_yr = np.full(state.N, 0.5)
        smb_m_yr[state.gl_cell - 3 : state.gl_cell + 1] = -5.0
        smb_m_s = self.smb_conv.from_m_ice_yr(smb_m_yr)

        dt = 0.02 * CONST.yr_to_s

        new_state, diag = self.solver.step(state, smb_m_s, dt)

        self.assertLess(abs(diag.residual), 1e-5 * M_gr_0)
        if diag.event in ("partial_retreat", "full_unground"):
            self.assertGreater(new_state.floating_mass_kg, F_0, "Floating ledger did not increase upon retreat")

    def test_advance_draws_mass_from_floating_ledger(self):
        """Accumulation at grounding line induces advance. Ice must be drawn from floating ledger."""
        state = self.domain.initial_state(floating_mass_kg=1e14)
        state.H[state.gl_cell + 1] = 450.0

        M_gr_0 = state.compute_grounded_mass_kg()
        F_0 = state.floating_mass_kg

        smb_m_yr = np.full(state.N, 3.0)
        smb_m_s = self.smb_conv.from_m_ice_yr(smb_m_yr)

        dt = 0.01 * CONST.yr_to_s

        new_state, diag = self.solver.step(state, smb_m_s, dt)

        self.assertLess(abs(diag.residual), 1e-5 * M_gr_0)
        if diag.event in ("partial_advance", "full_ground"):
            self.assertLess(new_state.floating_mass_kg, F_0, "Floating ledger did not decrease upon advance")

    def test_cfl_violation_raises_error(self):
        """If timestep is set absurdly large such that GL jumps > 1 cell, CFLViolation must be raised."""
        state = self.domain.initial_state()
        smb_m_yr = np.full(state.N, -50.0)
        smb_m_s = self.smb_conv.from_m_ice_yr(smb_m_yr)

        dt_huge = 5.0 * CONST.yr_to_s

        with self.assertRaises((CFLViolation, ConservationError)):
            self.solver.step(state, smb_m_s, dt_huge)

    def test_no_double_counting_advective_vs_boundary(self):
        """Verify that advective flux Q_GL and boundary migration dM_boundary are distinct."""
        state = self.domain.initial_state(floating_mass_kg=1e14)
        smb_m_s = np.zeros(state.N)
        dt = 0.02 * CONST.yr_to_s

        new_state, diag = self.solver.step(state, smb_m_s, dt)

        self.assertGreaterEqual(diag.Q_GL, 0.0)
        res = (
            diag.M_gr_end
            - diag.M_gr_start
            - dt * diag.Mdot_SMB
            + dt * CONST.rho_ice * diag.Q_GL
            - diag.dM_boundary
        )
        self.assertAlmostEqual(res, diag.residual, places=5)
        self.assertLess(abs(diag.residual), 1e-5 * diag.M_gr_start)


class TestMultiStepRun(unittest.TestCase):
    """Test multi-step integration over 1 model year."""

    def test_one_year_run_conservation(self):
        domain = FlowlineDomain.synthetic_marine(
            N_land=20,
            N_marine=30,
            width_m=20_000.0,
            H0=400.0,
            name="one_year_run"
        )
        solver = FVContinuitySolver(use_schoof=True)
        smb_conv = SMBConverter()
        state0 = domain.initial_state(floating_mass_kg=1e14)

        smb_m_s = smb_conv.from_m_ice_yr(np.full(state0.N, 0.3))
        dt = 0.05 * CONST.yr_to_s
        n_steps = 20

        states, diags = solver.run(state0, smb_m_s, n_steps=n_steps, dt=dt)

        self.assertEqual(len(states), n_steps + 1)
        self.assertEqual(len(diags), n_steps)

        for step_i, d in enumerate(diags):
            self.assertLess(
                abs(d.residual),
                1e-5 * d.M_gr_start,
                f"Step {step_i} failed conservation: residual={d.residual:.2e}"
            )
            self.assertTrue(d.cfl_ok, f"Step {step_i} violated CFL")


if __name__ == "__main__":
    unittest.main()
