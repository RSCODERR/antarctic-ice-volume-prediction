"""
tests/test_stage4_4_2_synthetic_conservation.py
================================================
Executable unittest test suite for Phase 5 — Stage 4.4.2:
Synthetic Conservation Suite Execution.

Tests cover:
  1. test_test1_shared_face_flux_cancellation
  2. test_test2_amr_interface_conservation
  3. test_test3_cut_cell_conservation
  4. test_test4_moving_grounding_line_mass_accounting
  5. test_test5_wgs84_metric_conversion_invariance
  6. test_test6_vaf_closed_budget
  7. test_additional_scientific_checks (ocean drag, slope screening, membrane coupling, cut-cell benchmark)
"""

from __future__ import annotations
import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.physics.synthetic_conservation import (
    run_test1_shared_face_flux_cancellation,
    run_test2_amr_interface_conservation,
    run_test3_cut_cell_conservation,
    run_test4_moving_grounding_line_mass_accounting,
    run_test5_wgs84_metric_conversion_invariance,
    run_test6_vaf_closed_budget,
    check_ocean_drag_scaling_m_s,
    check_slope_screening_operational_rule,
    verify_partial_cell_membrane_transmission,
    compare_homogenized_vs_cut_cell_benchmark,
)


class TestStage442SyntheticConservation(unittest.TestCase):
    """Execution suite for the 6 Stage 4.4.2 conservation benchmarks."""

    def test_test1_shared_face_flux_cancellation(self) -> None:
        """TEST-1: Every internal face satisfies F(I->J) + F(J->I) = 0 (< 1e-15 in both mass kg/s and vol m^3/s)."""
        res = run_test1_shared_face_flux_cancellation()
        self.assertTrue(res.passed, f"TEST-1 failed: {res.numerical_actual}")
        self.assertLess(res.relative_residual, 1.0e-15)
        self.assertEqual(res.details["max_pairwise_v_err"], 0.0)
        self.assertEqual(res.details["max_pairwise_h_err"], 0.0)
        self.assertEqual(res.details["max_pairwise_vol_v_err"], 0.0)
        self.assertEqual(res.details["max_pairwise_vol_h_err"], 0.0)

    def test_test2_amr_interface_conservation(self) -> None:
        """TEST-2: AMR 2:1 interface matching F_macro = F_sub1 + F_sub2 (< 1e-14 kg/s, < 1.1e-17 m^3/s)."""
        res = run_test2_amr_interface_conservation()
        self.assertTrue(res.passed, f"TEST-2 failed: {res.numerical_actual}")
        self.assertLess(res.absolute_residual, 1.0e-14)
        self.assertLess(res.details["abs_residual_vol_m3_s"], 1.1e-17)
        self.assertGreater(res.details["naive_discretization_mismatch_kg_s"], 1.0e-10)

    def test_test3_cut_cell_conservation(self) -> None:
        """TEST-3: Partial cut-cell divergence theorem conservation (< 1e-14 kg/s, < 1.1e-17 m^3/s)."""
        res = run_test3_cut_cell_conservation()
        self.assertTrue(res.passed, f"TEST-3 failed: {res.numerical_actual}")
        self.assertLess(res.absolute_residual, 1.0e-14)
        self.assertLess(res.details["exact_vol_residual_m3_s"], 1.1e-17)
        self.assertGreater(res.details["naive_relative_error"], 0.10)
        self.assertEqual(res.details["smb_m_yr_ice_eq"], 0.5)

    def test_test4_moving_grounding_line_mass_accounting(self) -> None:
        """TEST-4: Bilateral cryosphere mass accounting during GL retreat (< 1e-12)."""
        res = run_test4_moving_grounding_line_mass_accounting()
        self.assertTrue(res.passed, f"TEST-4 failed: {res.numerical_actual}")
        self.assertLess(res.relative_residual, 1.0e-12)
        self.assertGreaterEqual(res.details["cells_retreated"], 5)
        self.assertGreater(res.details["total_reclassified_mass_kg"], 0.0)

    def test_test5_wgs84_metric_conversion_invariance(self) -> None:
        """TEST-5: WGS84 single-metric scaling & metric-consistent streamfunction (< 1e-14)."""
        res = run_test5_wgs84_metric_conversion_invariance(N_steps=40)
        self.assertTrue(res.passed, f"TEST-5 failed: {res.numerical_actual}")
        self.assertLess(res.relative_residual, 1.0e-14)
        self.assertLess(res.details["vortex_relative_volume_error"], 1.0e-14)
        self.assertEqual(res.details["max_metric_div_u_phys_analytic"], 0.0)
        self.assertGreater(res.details["max_metric_div_u_proj_analytic_s_inv"], 1.0e-13)
        self.assertGreater(res.details["omitted_metric_drift_fraction"], 1.0e-2)

    def test_test6_vaf_closed_budget(self) -> None:
        """TEST-6: Discrete VAF closed budget d(VAF)/dt = SMB_g - Q_GL (< 1e-12 with discrete remap)."""
        res = run_test6_vaf_closed_budget(T_years=20.0)
        self.assertTrue(res.passed, f"TEST-6 failed: {res.numerical_actual}")
        self.assertLess(res.relative_residual, 1.0e-12)
        self.assertGreater(res.details["rel_naive_leibniz_error"], 1.0e-3)

    def test_additional_scientific_checks(self) -> None:
        """Verify the 4 additional scientific checks from Stage 4.4.2 prompt."""
        # 1. Ocean drag scaling with consistent m/s units
        drag_res = check_ocean_drag_scaling_m_s()
        self.assertLess(drag_res["max_drag_uw0_Pa"], 1.0e-8)
        self.assertLess(drag_res["max_drag_uw005_Pa"], 1.0e-1)

        # 2. Slope screening operational rule
        slope_res = check_slope_screening_operational_rule()
        self.assertEqual(slope_res["screening_threshold_rad"], 0.10)
        self.assertGreater(len(slope_res["why_not_guaranteed_99_pct"]), 2)

        # 3. Partial-cell membrane stress transmission
        mem_res = verify_partial_cell_membrane_transmission()
        self.assertTrue(mem_res["decoupled_membrane_continuous"])
        self.assertTrue(mem_res["naive_membrane_severed"])

        # 4. Homogenized vs Cut-Cell benchmark
        bench_res = compare_homogenized_vs_cut_cell_benchmark()
        self.assertAlmostEqual(bench_res["area_err_macro"], 0.0, places=5)
        self.assertGreater(bench_res["homogenized_boundary_flux_error_pct"], 1.0)
        self.assertEqual(bench_res["cut_cell_boundary_flux_error_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
