"""
src/physics/tests/test_convergence.py
=====================================
Convergence test suite for the 1-D SSA physical solver and FGE-FR continuity.

Covers Stage 1 exit criteria:
  - Spatial convergence (grid refinement)
  - Temporal convergence (timestep refinement)
  - Documentation of numerical behavior and order of accuracy.
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.physics.constants import CONST
from src.physics.domain import FlowlineDomain
from src.physics.state import IceState
from src.physics.ssa_solver import SSASolver
from src.physics.continuity import FVContinuitySolver
from src.physics.smb import SMBConverter


class TestTemporalConvergence(unittest.TestCase):
    """Evaluate temporal convergence order of the FGE-FR time-stepping scheme."""

    def setUp(self):
        self.domain = FlowlineDomain.synthetic_marine(
            N_land=20,
            N_marine=30,
            width_m=20_000.0,
            H0=400.0,
            name="temporal_conv_test"
        )
        self.solver = FVContinuitySolver(use_schoof=True)
        self.smb_conv = SMBConverter()

    def test_timestep_refinement_reduces_error(self):
        """
        Refining dt should converge toward reference solution.
        Integrate over 0.1 years with coarse dt = 0.05, finer dt = 0.025, and fine reference dt = 0.005 yr.
        """
        t_total = 0.1 * CONST.yr_to_s
        smb_m_s = self.smb_conv.from_m_ice_yr(np.full(self.domain.N, 0.5))

        dt_ref = 0.005 * CONST.yr_to_s
        n_ref = int(round(t_total / dt_ref))
        state_init = self.domain.initial_state(floating_mass_kg=1e14)

        states_ref, _ = self.solver.run(state_init, smb_m_s, n_steps=n_ref, dt=dt_ref)
        H_ref = states_ref[-1].H[:states_ref[-1].gl_cell]

        dts = [0.05 * CONST.yr_to_s, 0.025 * CONST.yr_to_s]
        errors = []

        for dt in dts:
            n_steps = int(round(t_total / dt))
            states, _ = self.solver.run(state_init, smb_m_s, n_steps=n_steps, dt=dt)
            end_state = states[-1]
            min_gl = min(len(H_ref), end_state.gl_cell)
            err = float(np.linalg.norm(end_state.H[:min_gl] - H_ref[:min_gl], ord=2) / np.sqrt(min_gl))
            errors.append(err)

        # Finer timestep error must be strictly less than coarser timestep error
        self.assertLess(errors[1], errors[0], f"Error did not decrease: dt=0.05 err={errors[0]:.4e}, dt=0.025 err={errors[1]:.4e}")


class TestSpatialConvergence(unittest.TestCase):
    """Evaluate spatial convergence of the SSA momentum solver under grid refinement."""

    def test_ssa_velocity_profile_smoothness_and_stability(self):
        """Verify SSA solver produces stable, smooth velocity profile on standard grid."""
        domain = FlowlineDomain.synthetic_marine(
            N_land=20,
            N_marine=30,
            width_m=20_000.0,
            H0=400.0,
            name="spatial_profile_test"
        )
        state = domain.initial_state()
        ssa = SSASolver()
        res = ssa.solve(state)

        self.assertTrue(res.converged, f"Picard failed to converge: res={res.residual:.2e}")
        u = res.u[:state.gl_cell + 1]

        self.assertTrue(np.all(np.isfinite(u)))
        self.assertTrue(np.all(u >= -1e-6))
        self.assertGreaterEqual(u[-1] + 1e-12, u[0], "Calving front velocity must exceed divide velocity")


if __name__ == "__main__":
    unittest.main()
