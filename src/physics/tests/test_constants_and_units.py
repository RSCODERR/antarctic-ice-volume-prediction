"""
src/physics/tests/test_constants_and_units.py
=============================================
Test dimensional consistency of all physical constants and derived quantities.

Covers Stage 1 exit criterion:
  "All dimensional and unit tests pass."

No physical parameters are calibrated.  Every assertion is derivable from
first principles using published SI unit conversions.
"""

import unittest
import dataclasses
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.physics.constants import PhysicsConstants, CONST
from src.physics.rheology import GlensFlowLaw
from src.physics.basal_drag import BasalDrag
from src.physics.lateral_drag import LateralDrag
from src.physics.grounding_line import SchoofGLFlux
from src.physics.smb import SMBConverter


class TestPhysicsConstants(unittest.TestCase):
    """Unit tests for PhysicsConstants."""

    def test_singleton_is_frozen(self):
        """CONST must be immutable."""
        with self.assertRaises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
            CONST.rho_ice = 999.0

    def test_yr_to_s_value(self):
        """365.25 * 24 * 3600 = 31 557 600 s yr⁻¹."""
        self.assertAlmostEqual(CONST.yr_to_s, 31_557_600.0, delta=1.0)

    def test_s_to_yr_reciprocal(self):
        """s_to_yr · yr_to_s = 1."""
        self.assertAlmostEqual(CONST.s_to_yr * CONST.yr_to_s, 1.0, places=12)

    def test_domain_dx(self):
        """Frozen grid spacing = 500 m."""
        self.assertEqual(CONST.domain_dx, 500.0)

    def test_domain_n_cells(self):
        """Frozen cell count = 866 358."""
        self.assertEqual(CONST.domain_n_cells, 866_358)

    def test_domain_area_km2(self):
        """Frozen area = 216 062.17 km²."""
        self.assertAlmostEqual(CONST.domain_area_km2, 216_062.17, delta=0.01)

    def test_rho_ratio(self):
        """ρ_w / ρ_i > 1 (water denser than ice)."""
        self.assertGreater(CONST.rho_water / CONST.rho_ice, 1.0)

    def test_flotation_thickness_above_sl(self):
        """Above sea level bed → H_crit = 0."""
        H_crit = CONST.flotation_thickness(z_sl=0.0, z_bed=100.0)
        self.assertEqual(H_crit, 0.0)

    def test_flotation_thickness_below_sl(self):
        """H_crit = (ρ_w/ρ_i)(z_sl - z_bed) for z_bed < z_sl."""
        z_bed = -500.0
        z_sl = 0.0
        H_crit = CONST.flotation_thickness(z_sl, z_bed)
        expected = (CONST.rho_water / CONST.rho_ice) * 500.0
        self.assertAlmostEqual(H_crit, expected, places=9)

    def test_B_from_A(self):
        """B = A^(-1/n) must satisfy B^n · A = 1."""
        B = CONST.B()
        self.assertAlmostEqual(B ** CONST.glen_n * CONST.A_default, 1.0, places=6)

    def test_u_reg_in_m_per_yr(self):
        """u_reg ≈ 1×10⁻⁴ m yr⁻¹ → 3.17×10⁻¹² m s⁻¹."""
        u_reg_m_yr = CONST.u_reg * CONST.yr_to_s
        self.assertAlmostEqual(u_reg_m_yr, 1e-4, places=6)

    def test_u_scale_in_m_per_yr(self):
        """u_scale ≈ 10 m yr⁻¹."""
        u_scale_yr = CONST.u_scale * CONST.yr_to_s
        self.assertAlmostEqual(u_scale_yr, 10.0, places=2)

    def test_dt_target_in_yr(self):
        """dt_target ≈ 0.05 yr."""
        dt_yr = CONST.dt_target * CONST.s_to_yr
        self.assertAlmostEqual(dt_yr, 0.05, places=6)


class TestBasalDragUnits(unittest.TestCase):
    """Dimensional audit for basal drag — Phase 5.2.1 audit values."""

    def setUp(self):
        self.bd = BasalDrag()

    def test_beta_at_rest_magnitude(self):
        """
        β(0) = C_bed · u_reg^(m-1) ≈ 4.634×10¹⁴ Pa s m⁻¹.

        Phase 5.2.1 audit & Phase 5.2.2 blueprint confirmed value.
        """
        beta0 = self.bd.beta_at_rest()
        expected = 1e7 * (3.17e-12) ** (1.0 / 3.0 - 1.0)
        self.assertLess(abs(beta0 - expected) / expected, 0.01)

    def test_beta_at_rest_order_of_magnitude(self):
        """β(0) must be in the range 10¹⁴ to 10¹⁵ Pa s m⁻¹."""
        beta0 = self.bd.beta_at_rest()
        self.assertGreater(beta0, 1e14)
        self.assertLess(beta0, 1e15)

    def test_tau_b_at_1ms_equals_C_bed(self):
        """
        τ_b(u=1 m/s) = C_bed · 1^(m-1) · 1 = C_bed  [Pa].

        For m = 1/3: (1²+u_reg²)^((m-1)/2) · 1 ≈ 1  when u >> u_reg.
        """
        u = np.array([1.0])
        tau = self.bd.tau_b(u)[0]
        self.assertLess(abs(tau - self.bd.C_bed) / self.bd.C_bed, 1e-6)

    def test_tau_b_sign(self):
        """τ_b > 0 for u > 0 (basal drag opposes positive flow)."""
        u = np.array([0.1, 1.0, 100.0])
        tau = self.bd.tau_b(u)
        self.assertTrue(np.all(tau > 0.0))

    def test_tau_b_negative_u(self):
        """τ_b < 0 for u < 0 (basal drag opposes negative flow)."""
        u = np.array([-0.1, -1.0])
        tau = self.bd.tau_b(u)
        self.assertTrue(np.all(tau < 0.0))

    def test_beta_positive(self):
        """Linearised β must always be positive (viscous-like drag)."""
        u = np.array([0.0, 0.1, 1.0, 100.0])
        beta = self.bd.beta_linearised(u)
        self.assertTrue(np.all(beta > 0.0))

    def test_units_dict(self):
        """verify_units() must return dict with expected keys."""
        d = self.bd.verify_units()
        self.assertIn("C_bed [Pa (m/s)^(-1/3)]", d)
        self.assertIn("beta_at_rest [Pa s/m]", d)


class TestRheologyUnits(unittest.TestCase):
    """Test Glen's flow law effective viscosity dimensions."""

    def setUp(self):
        self.rh = GlensFlowLaw()

    def test_B_units_order(self):
        """B = A^(-1/n) for A=3.5e-25 Pa⁻³ s⁻¹, n=3 → B ≈ 1.5e8 Pa s^(1/3)."""
        self.assertGreater(self.rh.B, 1e7)
        self.assertLess(self.rh.B, 1e10)

    def test_nu_at_zero_strain_rate(self):
        """ν_eff must be finite at du/dx = 0 due to regularisation."""
        du_dx = np.array([0.0])
        nu = self.rh.effective_viscosity(du_dx)
        self.assertTrue(np.isfinite(nu[0]))
        self.assertGreater(nu[0], 0.0)

    def test_nu_decreases_with_strain_rate(self):
        """Shear-thinning: higher strain rate → lower viscosity."""
        du_dx = np.array([1e-10, 1e-8, 1e-6, 1e-4])
        nu = self.rh.effective_viscosity(du_dx)
        self.assertLess(nu[-1], nu[0])

    def test_nu_units_order(self):
        """ν_eff should be ~10¹² to 10¹⁸ Pa s for typical Antarctic ice."""
        du_dx = np.array([1e-9])
        nu = self.rh.effective_viscosity(du_dx)
        self.assertGreater(nu[0], 1e10)
        self.assertLess(nu[0], 1e18)


class TestLateralDragUnits(unittest.TestCase):
    """Test lateral drag — Phase 5.2.2.5 confirmed formula."""

    def setUp(self):
        self.ld = LateralDrag()

    def test_shape_factor_is_5(self):
        """Phase 5.2.2.5: shape factor = 5 (no factor of 2 in denominator)."""
        self.assertEqual(self.ld.shape_factor, 5.0)

    def test_tau_wall_positive(self):
        """τ_wall ≥ 0 for any u."""
        u = np.array([1.0, 10.0, 100.0]) / CONST.yr_to_s
        W = np.array([2e4, 2e4, 2e4])
        tw = self.ld.tau_wall(u, W)
        self.assertTrue(np.all(tw >= 0.0))

    def test_tau_wall_increases_with_velocity(self):
        """Higher velocity → higher wall shear stress."""
        u = np.array([1.0, 10.0, 100.0]) / CONST.yr_to_s
        W = np.full(3, 2e4)
        tw = self.ld.tau_wall(u, W)
        self.assertGreater(tw[2], tw[1])
        self.assertGreater(tw[1], tw[0])

    def test_lateral_body_force_sign(self):
        """Lateral body force opposes flow direction."""
        u_pos = np.array([10.0 / CONST.yr_to_s])
        u_neg = np.array([-10.0 / CONST.yr_to_s])
        W = np.array([2e4])
        H = np.array([500.0])
        f_pos = self.ld.lateral_body_force(u_pos, W, H)
        f_neg = self.ld.lateral_body_force(u_neg, W, H)
        self.assertGreater(f_pos[0], 0.0)
        self.assertLess(f_neg[0], 0.0)

    def test_lateral_body_force_scales_linearly_with_thickness(self):
        """Phase 5 Stage 2.1 correction: f_lat = (2 H / W) * tau_wall."""
        u = np.array([100.0 / CONST.yr_to_s])
        W = np.array([4000.0])
        f_H300 = self.ld.lateral_body_force(u, W, H=300.0)[0]
        f_H600 = self.ld.lateral_body_force(u, W, H=600.0)[0]
        self.assertAlmostEqual(f_H600 / f_H300, 2.0, places=10)

    def test_lateral_drag_dimensional_consistency(self):
        """Verify lateral resisting stress has units of Pascals [N m^-2]."""
        u = np.array([100.0 / CONST.yr_to_s])
        W = np.array([3800.0])
        H = np.array([241.0])
        tw = self.ld.tau_wall(u, W)[0]
        flat = self.ld.lateral_body_force(u, W, H)[0]
        expected_stress = (2.0 * 241.0 / 3800.0) * tw
        self.assertAlmostEqual(flat, expected_stress, places=10)

    def test_no_factor_2_in_denominator_of_tau_wall(self):
        """
        Verify the formula is (5 u / AW)^(1/n), not (5 u / (2AW))^(1/n).
        """
        u_val = 100.0 / CONST.yr_to_s
        W_val = 2e4
        A = CONST.A_default
        n = CONST.glen_n
        u = np.array([u_val])
        W = np.array([W_val])
        tw_actual = self.ld.tau_wall(u, W)[0]
        tw_correct = (5.0 * u_val / (A * W_val)) ** (1.0 / n)
        tw_wrong = (5.0 * u_val / (2.0 * A * W_val)) ** (1.0 / n)
        self.assertLess(abs(tw_actual - tw_correct) / tw_correct, 1e-10)
        self.assertGreater(abs(tw_actual - tw_wrong) / tw_wrong, 0.1)


class TestSMBConverterUnits(unittest.TestCase):
    """Test SMB unit conversions are dimensionally correct."""

    def setUp(self):
        self.smb = SMBConverter()

    def test_kg_m2_s_to_m_s(self):
        """RACMO native instantaneous variable: kg m^-2 s^-1 -> m s^-1 ice eq."""
        raw_val = 1.0e-4 # kg m^-2 s^-1
        result = self.smb.from_kg_m2_s(np.array([raw_val]))[0]
        expected = raw_val / CONST.rho_ice
        self.assertLess(abs(result - expected) / expected, 1e-10)

    def test_kg_m2_yr_to_m_s(self):
        result = self.smb.from_kg_m2_yr(np.array([1000.0]))[0]
        expected = 1000.0 / (CONST.rho_ice * CONST.yr_to_s)
        self.assertLess(abs(result - expected) / expected, 1e-10)

    def test_m_ice_yr_to_m_s(self):
        result = self.smb.from_m_ice_yr(np.array([1.0]))[0]
        expected = 1.0 / CONST.yr_to_s
        self.assertLess(abs(result - expected) / expected, 1e-10)

    def test_mm_we_yr_to_m_s(self):
        result = self.smb.from_mm_we_yr(np.array([1.0]))[0]
        result_kg = self.smb.from_kg_m2_yr(np.array([1.0]))[0]
        self.assertLess(abs(result - result_kg) / result_kg, 1e-10)

    def test_roundtrip_conversions(self):
        """Test roundtrip fidelity for all supported representations."""
        test_m_s = 3.4556257e-8 # approx 1000 mm w.e. / yr
        
        # kg m^-2 s^-1 roundtrip
        val_kg_s = self.smb.to_kg_m2_s(test_m_s)
        rec_m_s_1 = self.smb.from_kg_m2_s(val_kg_s)
        self.assertAlmostEqual(test_m_s, rec_m_s_1, places=15)

        # kg m^-2 yr^-1 roundtrip
        val_kg_yr = self.smb.to_kg_m2_yr(test_m_s)
        rec_m_s_2 = self.smb.from_kg_m2_yr(val_kg_yr)
        self.assertAlmostEqual(test_m_s, rec_m_s_2, places=15)

        # mm w.e. yr^-1 roundtrip
        val_mm_yr = self.smb.to_mm_we_yr(test_m_s)
        rec_m_s_3 = self.smb.from_mm_we_yr(val_mm_yr)
        self.assertAlmostEqual(test_m_s, rec_m_s_3, places=15)

        # m ice yr^-1 roundtrip
        val_m_yr = self.smb.to_m_ice_yr(test_m_s)
        rec_m_s_4 = self.smb.from_m_ice_yr(val_m_yr)
        self.assertAlmostEqual(test_m_s, rec_m_s_4, places=15)

    def test_cell_volume_source_units(self):
        smb_m_s = self.smb.from_m_ice_yr(np.array([0.5]))
        S = self.smb.cell_volume_source(smb_m_s, np.array([2e4]), 500.0)
        expected = 0.5 * 2e4 * 500.0 / CONST.yr_to_s
        self.assertLess(abs(S[0] - expected) / expected, 1e-10)

    def test_total_smb_mass_flux_units(self):
        N = 10
        smb_m_s = self.smb.from_m_ice_yr(np.full(N, 0.5))
        W = np.full(N, 2e4)
        Mdot = self.smb.total_smb_mass_flux(smb_m_s, W, 500.0, n_grounded=N)
        expected = CONST.rho_ice * 0.5 / CONST.yr_to_s * 2e4 * 500.0 * N
        self.assertLess(abs(Mdot - expected) / expected, 1e-10)


class TestSchoofGLFluxUnits(unittest.TestCase):
    """Test Schoof GL flux dimensional consistency."""

    def setUp(self):
        self.gl = SchoofGLFlux()

    def test_q_gl_increases_with_H(self):
        q1 = self.gl.q_gl(500.0)
        q2 = self.gl.q_gl(1000.0)
        ratio = q2 / q1
        # (1000/500)^4.75 = 2^4.75 ≈ 26.91
        self.assertLess(abs(ratio - 26.91), 1.0)

    def test_q_gl_zero_thickness(self):
        self.assertEqual(self.gl.q_gl(0.0), 0.0)

    def test_Q_gl_proportional_to_width(self):
        Q1 = self.gl.Q_gl(500.0, 1e4)
        Q2 = self.gl.Q_gl(500.0, 2e4)
        self.assertLess(abs(Q2 / Q1 - 2.0), 1e-10)

    def test_mass_flux_uses_rho_i(self):
        Q = self.gl.Q_gl(500.0, 2e4)
        M = self.gl.mass_flux(500.0, 2e4)
        self.assertLess(abs(M / (CONST.rho_ice * Q) - 1.0), 1e-10)

    def test_sensitivity_formula(self):
        H = 500.0
        dH = 0.1
        numerical = (self.gl.q_gl(H + dH) - self.gl.q_gl(H)) / dH
        analytic = self.gl.sensitivity(H, dH)
        self.assertLess(abs(numerical - analytic) / analytic, 0.005)


if __name__ == "__main__":
    unittest.main()
