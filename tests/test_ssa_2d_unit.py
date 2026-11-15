"""
tests/test_ssa_2d_unit.py
=========================
Unit tests for the 2D SSA solver components:
  1. Constitutive relations and strain-rate tensor invariants.
  2. Non-linear Glen effective viscosity and regularisation.
  3. Basal traction, Weertman power law, and flotation shut-off.
  4. Marine calving front depth-integrated boundary conditions.
  5. Sparse matrix assembly and boundary condition row enforcement.
  6. Non-linear solver convergence and rollback safeguards.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import numpy as np

from src.physics.ssa_2d.constants import (
    SSA2DConstants,
    CONST_DEFAULT,
    CONST_MISMIP,
)
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.rheology import (
    compute_strain_rates_2d,
    compute_effective_strain_rate_sq,
    compute_effective_viscosity_2d,
)
from src.physics.ssa_2d.friction import (
    compute_flotation_fraction_and_surface,
    compute_basal_drag_coefficient,
)
from src.physics.ssa_2d.boundary import compute_calving_front_traction
from src.physics.ssa_2d.assembly import assemble_ssa_system_2d
from src.physics.ssa_2d.solver import SSASolver2D, NonlinearConvergenceError


class TestSSA2DUnit(unittest.TestCase):
    """Unit test suite for 2D SSA physics and solver modules."""

    def setUp(self) -> None:
        self.const = CONST_DEFAULT
        self.grid = Grid2D(Lx=20_000.0, Ly=10_000.0, Nx=10, Ny=5)

    def test_constitutive_strain_rate_invariants(self) -> None:
        """Test effective strain rate invariant against hand-calculated tensor invariants."""
        eps_0 = 1.0e-10

        # Case A: Pure uniaxial extension: eps_xx = 1e-4, eps_yy = 0, eps_xy = 0
        eps_xx = np.array([1.0e-4])
        eps_yy = np.array([0.0])
        eps_xy = np.array([0.0])
        eps_e_sq = compute_effective_strain_rate_sq(eps_xx, eps_yy, eps_xy, eps_0=eps_0)
        expected = (1.0e-4)**2 + eps_0**2
        self.assertAlmostEqual(float(eps_e_sq[0]), expected, places=12)

        # Case B: Pure shear: du/dy = 2e-4, dv/dx = 0 -> eps_xy = 1e-4, eps_xx = eps_yy = 0
        eps_xx = np.array([0.0])
        eps_yy = np.array([0.0])
        eps_xy = np.array([1.0e-4])
        eps_e_sq = compute_effective_strain_rate_sq(eps_xx, eps_yy, eps_xy, eps_0=eps_0)
        expected = (1.0e-4)**2 + eps_0**2
        self.assertAlmostEqual(float(eps_e_sq[0]), expected, places=12)

        # Case C: General combined 2D tensor: eps_xx = 2e-4, eps_yy = -1e-4, eps_xy = 1.5e-4
        # eps_e^2 = eps_xx^2 + eps_yy^2 + eps_xx * eps_yy + eps_xy^2 + eps_0^2
        # = 4e-8 + 1e-8 - 2e-8 + 2.25e-8 = 5.25e-8
        eps_xx = np.array([2.0e-4])
        eps_yy = np.array([-1.0e-4])
        eps_xy = np.array([1.5e-4])
        eps_e_sq = compute_effective_strain_rate_sq(eps_xx, eps_yy, eps_xy, eps_0=0.0)
        self.assertAlmostEqual(float(eps_e_sq[0]), 5.25e-8, places=14)

    def test_viscosity_glen_law_and_regularisation(self) -> None:
        """Test Glen flow law effective viscosity, regularisation limit, and shear thinning."""
        grid = Grid2D(Lx=10_000.0, Ly=10_000.0, Nx=4, Ny=4)
        u_zero = np.zeros((4, 4), dtype=np.float64)
        v_zero = np.zeros((4, 4), dtype=np.float64)

        # 1. At zero strain rate, viscosity should equal the regularised upper limit
        # nu_0 = 0.5 * A^(-1/3) * (eps_0^2)^(-1/3) = 0.5 * A^(-1/3) * eps_0^(-2/3)
        nu_zero = compute_effective_viscosity_2d(u_zero, v_zero, grid, self.const)
        expected_nu_0 = 0.5 * (self.const.glen_A ** (-1.0 / 3.0)) * (self.const.eps_0 ** (-2.0 / 3.0))
        np.testing.assert_allclose(nu_zero, expected_nu_0, rtol=1e-5)

        # 2. Shear thinning scaling test (n=3):
        # Viscosity scales as (eps_e)^(-2/3). Doubling strain rate reduces nu by 2^(-2/3) ~ 0.62996.
        u1 = np.ones((4, 4), dtype=np.float64) * 0.01
        # Set a linear velocity field u = gamma * x
        gamma1 = 1.0e-8  # s^-1 (well above eps_0 = 1e-10)
        u1 = gamma1 * grid.X
        nu1 = compute_effective_viscosity_2d(u1, v_zero, grid, self.const)

        u2 = 2.0 * gamma1 * grid.X
        nu2 = compute_effective_viscosity_2d(u2, v_zero, grid, self.const)

        # Interior ratio
        ratio = nu2[1, 1] / nu1[1, 1]
        expected_ratio = 2.0 ** (-2.0 / 3.0)
        self.assertAlmostEqual(ratio, expected_ratio, delta=1e-3)

    def test_basal_traction_weertman_and_flotation(self) -> None:
        """Test Weertman sliding exponent, regularisation, and flotation shut-off."""
        Ny, Nx = 5, 5
        u = np.zeros((Ny, Nx), dtype=np.float64)
        v = np.zeros((Ny, Nx), dtype=np.float64)
        f_gr = np.ones((Ny, Nx), dtype=np.float64)

        # 1. Zero velocity limit: beta_b = C_bed * (u_0)^(-2/3)
        beta_0 = compute_basal_drag_coefficient(u, v, f_gr, self.const.C_bed, self.const)
        expected_beta_0 = self.const.C_bed * (self.const.u_0 ** (-2.0 / 3.0))
        np.testing.assert_allclose(beta_0, expected_beta_0, rtol=1e-7)

        # 2. Weertman power law test (m = 1/3):
        # For |u| >> u_0, tau_b = beta_b * u = C_bed * u^(1/3).
        # Multiplying u by 8 increases tau_b by 8^(1/3) = 2.0.
        u1 = np.ones((Ny, Nx), dtype=np.float64) * 1.0e-5  # ~ 315 m/yr
        u2 = np.ones((Ny, Nx), dtype=np.float64) * 8.0e-5
        beta1 = compute_basal_drag_coefficient(u1, v, f_gr, self.const.C_bed, self.const)
        beta2 = compute_basal_drag_coefficient(u2, v, f_gr, self.const.C_bed, self.const)

        tau1 = beta1[2, 2] * u1[2, 2]
        tau2 = beta2[2, 2] * u2[2, 2]
        self.assertAlmostEqual(tau2 / tau1, 2.0, delta=1e-4)

        # 3. Flotation shut-off test: on floating ice (f_gr = 0), beta_b MUST be identically 0.0
        f_gr_flot = np.zeros((Ny, Nx), dtype=np.float64)
        beta_flot = compute_basal_drag_coefficient(u1, v, f_gr_flot, self.const.C_bed, self.const)
        np.testing.assert_allclose(beta_flot, 0.0, atol=1e-15)

    def test_calving_front_traction_and_dimensions(self) -> None:
        """Test marine calving front depth-integrated normal stress balance."""
        H_front = np.array([300.0, 400.0, 500.0], dtype=np.float64)
        b_front = np.array([-400.0, -450.0, -500.0], dtype=np.float64)
        is_flot = np.array([True, True, False], dtype=np.bool_)

        const = CONST_MISMIP
        N_nn = compute_calving_front_traction(H_front, b_front, is_flot, const)

        # Check floating cells (indices 0 and 1):
        # N_nn = 0.5 * rho_i * g * H^2 * (1 - rho_i / rho_w)
        for idx in (0, 1):
            H = H_front[idx]
            expected = 0.5 * const.rho_ice * const.g * (H**2) * (1.0 - (const.rho_ice / const.rho_water))
            self.assertAlmostEqual(N_nn[idx], expected, places=5)
            # Normal traction in tensile marine calving must be strictly positive [N/m]
            self.assertGreater(N_nn[idx], 0.0)

        # Check grounded tidewater cell (index 2):
        # N_nn = 0.5 * rho_i * g * H^2 - 0.5 * rho_w * g * d_w^2 with d_w = 500 m
        H = H_front[2]
        d_w = 500.0
        expected_ground = 0.5 * const.rho_ice * const.g * (H**2) - 0.5 * const.rho_water * const.g * (d_w**2)
        self.assertAlmostEqual(N_nn[2], expected_ground, places=5)

    def test_matrix_assembly_properties(self) -> None:
        """Test sparse matrix assembly dimensions, sparsity, and boundary condition enforcement."""
        grid = Grid2D(
            Lx=20_000.0, Ly=10_000.0, Nx=10, Ny=5,
            bc_west="divide", bc_east="calving_front", bc_south="no_slip", bc_north="no_slip"
        )
        H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 500.0
        b = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
        s = b + H
        nu = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 1.0e14
        beta_b = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 1.0e5

        A, rhs = assemble_ssa_system_2d(grid, H, s, b, nu, beta_b, self.const)

        N = grid.total_cells
        total_dofs = 2 * N
        self.assertEqual(A.shape, (total_dofs, total_dofs))
        self.assertEqual(len(rhs), total_dofs)

        # Sparsity check
        nnz = A.nnz
        sparsity = nnz / (total_dofs * total_dofs)
        self.assertLess(sparsity, 0.15)  # Highly sparse banded structure

        # Check West boundary (divide): u(0, j) must be pinned to 0
        for j in range(grid.Ny):
            ku = grid.dof_index_u(0, j)
            row = A.getrow(ku).toarray().ravel()
            self.assertEqual(row[ku], 1.0)
            self.assertEqual(np.count_nonzero(row), 1)
            self.assertEqual(rhs[ku], 0.0)

        # Check South boundary (no_slip): u(i, 0) = 0 and v(i, 0) = 0
        for i in range(grid.Nx):
            ku = grid.dof_index_u(i, 0)
            kv = grid.dof_index_v(i, 0)
            row_u = A.getrow(ku).toarray().ravel()
            row_v = A.getrow(kv).toarray().ravel()
            self.assertEqual(row_u[ku], 1.0)
            self.assertEqual(np.count_nonzero(row_u), 1)
            self.assertEqual(rhs[ku], 0.0)
            self.assertEqual(row_v[kv], 1.0)
            self.assertEqual(np.count_nonzero(row_v), 1)
            self.assertEqual(rhs[kv], 0.0)

    def test_solver_safeguards_and_rollback(self) -> None:
        """Test non-linear Picard solver convergence and rollback on iteration limit."""
        grid = Grid2D(Lx=20_000.0, Ly=10_000.0, Nx=8, Ny=4, bc_west="divide", bc_east="free_slip")
        H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 500.0
        b = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)

        # 1. Successful solve on flat geometry with zero driving stress
        solver = SSASolver2D(const=self.const, max_iter=20)
        res = solver.solve(grid, H, b, raise_on_failure=True)
        self.assertTrue(res.converged)
        self.assertLess(res.final_vel_step, 0.1)
        self.assertAlmostEqual(float(np.max(np.abs(res.u))), 0.0, places=12)

        # 2. Solver iteration limit test: when max_iter=1, it must fail to converge on active flow
        # Set a steep slope so that multiple Picard steps are required
        s_steep = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
        for i in range(grid.Nx):
            s_steep[:, i] = 1000.0 - 0.05 * grid.x_centers[i]
        b_steep = s_steep - H

        solver_tight = SSASolver2D(const=self.const, max_iter=1)
        with self.assertRaises(NonlinearConvergenceError):
            solver_tight.solve(grid, H, b_steep, s=s_steep, raise_on_failure=True)


if __name__ == "__main__":
    unittest.main()
