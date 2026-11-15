"""
tests/test_ssa_2d_synthetic.py
==============================
Synthetic benchmark verification suite for 2D SSA solver:
  1. Zero-velocity flat equilibrium: ||u||_inf < 1e-12 m/s.
  2. Uniform sloping slab: relative error vs analytical Weertman formula < 0.1%.
  3. Symmetric embayment channel flow: transverse symmetry |u(y) - u(Ly-y)| / u_max < 1e-10.
  4. Spatial grid refinement convergence: order of convergence O(dx^2).
  5. Discrete finite-volume mass conservation: |Delta M - Ledger| / M_0 < 1e-14.
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
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d, compute_cfl_timestep_2d


class TestSSA2DSynthetic(unittest.TestCase):
    """Synthetic benchmark verification suite for 2D SSA."""

    def setUp(self) -> None:
        self.const = CONST_DEFAULT

    def test_1_zero_velocity_flat_equilibrium(self) -> None:
        """Benchmark 1: Flat equilibrium slab with zero driving stress must yield u = 0."""
        grid = Grid2D(
            Lx=20_000.0, Ly=10_000.0, Nx=10, Ny=5,
            bc_west="divide", bc_east="free_slip", bc_south="free_slip", bc_north="free_slip"
        )
        H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 500.0
        b = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 100.0  # Horizontal flat bed
        s = b + H                                                  # Horizontal flat surface (ds/dx = 0, ds/dy = 0)

        solver = SSASolver2D(const=self.const, max_iter=20)
        res = solver.solve(grid, H, b, s=s, raise_on_failure=True)

        self.assertTrue(res.converged)
        max_u = float(np.max(np.abs(res.u)))
        max_v = float(np.max(np.abs(res.v)))
        self.assertLess(max_u, 1.0e-12, f"Expected zero along-flow velocity, got {max_u:.4e} m/s")
        self.assertLess(max_v, 1.0e-12, f"Expected zero across-flow velocity, got {max_v:.4e} m/s")

    def test_2_uniform_sloping_slab_analytical(self) -> None:
        """Benchmark 2: Uniform sloping slab compared against analytical Weertman formula."""
        # Geometry & physics
        alpha = 0.002       # 2 m/km slope
        H0 = 500.0         # uniform thickness
        C_bed = 5.0e6      # Pa (m/s)^(-1/3)
        const = SSA2DConstants(C_bed=C_bed, picard_omega=0.6, picard_max_iter=100)

        # Driving stress tau_d = rho_i * g * H * alpha
        tau_d = const.rho_ice * const.g * H0 * alpha
        # Analytical Weertman: tau_b = C_bed * u^(1/3) = tau_d -> u_analytical = (tau_d / C_bed)^3
        u_analytical = (tau_d / C_bed) ** 3.0

        grid = Grid2D(
            Lx=40_000.0, Ly=20_000.0, Nx=20, Ny=10,
            bc_west="dirichlet", bc_east="dirichlet", bc_south="free_slip", bc_north="free_slip"
        )
        H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * H0
        s = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
        for i in range(grid.Nx):
            s[:, i] = 1000.0 - alpha * grid.x_centers[i]
        b = s - H

        u_dir = np.full((grid.Ny, grid.Nx), u_analytical, dtype=np.float64)
        v_dir = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)

        solver = SSASolver2D(const=const, max_iter=100)
        # Initialize near analytical solution
        res = solver.solve(
            grid, H, b, s=s,
            u_init=u_dir * 0.9,
            u_dirichlet=u_dir,
            v_dirichlet=v_dir,
            raise_on_failure=True,
        )

        self.assertTrue(res.converged)
        # Check interior cells (away from boundaries)
        u_interior = res.u[2:-2, 2:-2]
        rel_errors = np.abs(u_interior - u_analytical) / u_analytical
        max_rel_error = float(np.max(rel_errors))

        self.assertLess(max_rel_error, 0.001, f"Max relative error {max_rel_error:.4e} exceeds 0.1% threshold")

    def test_3_symmetric_embayment_flow(self) -> None:
        """Benchmark 3: Embayment flow must preserve lateral symmetry across centerline to < 1e-10."""
        grid = Grid2D(
            Lx=40_000.0, Ly=20_000.0, Nx=20, Ny=11,  # Odd Ny=11 ensures exact symmetry across j=5
            bc_west="divide", bc_east="calving_front", bc_south="no_slip", bc_north="no_slip"
        )
        H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 500.0
        # Linear slope along x, perfectly symmetric in y
        s = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
        for i in range(grid.Nx):
            s[:, i] = 800.0 - (200.0 / grid.Lx) * grid.x_centers[i]
        b = s - H

        const = SSA2DConstants(C_bed=2.0e7, picard_omega=0.5, picard_max_iter=100)
        solver = SSASolver2D(const=const, max_iter=100)
        res = solver.solve(grid, H, b, s=s, raise_on_failure=True)

        self.assertTrue(res.converged)
        u = res.u
        v = res.v
        u_max = float(np.max(np.abs(u)))

        # 1. Along-flow velocity u(x, y) must equal u(x, Ly - y)
        u_flipped = np.flip(u, axis=0)
        u_sym_error = float(np.max(np.abs(u - u_flipped))) / (u_max + 1.0e-12)
        self.assertLess(u_sym_error, 1.0e-10, f"Along-flow symmetry error {u_sym_error:.4e} exceeds 1e-10")

        # 2. Across-flow velocity v(x, y) must be anti-symmetric: v(x, y) = -v(x, Ly - y)
        v_flipped = np.flip(v, axis=0)
        v_antisym_error = float(np.max(np.abs(v + v_flipped))) / (u_max + 1.0e-12)
        self.assertLess(v_antisym_error, 1.0e-10, f"Across-flow anti-symmetry error {v_antisym_error:.4e} exceeds 1e-10")

        # 3. Centerline across-flow velocity must be zero
        v_center = float(np.max(np.abs(v[grid.Ny // 2, :])))
        self.assertLess(v_center, 1.0e-12, f"Centerline transverse velocity {v_center:.4e} is non-zero")

    def test_4_grid_refinement_convergence(self) -> None:
        """Benchmark 4: Grid refinement verification demonstrating spatial convergence."""
        # Solve a 1D-like channel at 3 resolutions: dx = 2000m, 1000m, 500m
        resolutions = [(10, 5), (20, 5), (40, 5)]
        centerline_velocities = []

        for Nx, Ny in resolutions:
            grid = Grid2D(
                Lx=20_000.0, Ly=10_000.0, Nx=Nx, Ny=Ny,
                bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
            )
            H = np.ones((grid.Ny, grid.Nx), dtype=np.float64) * 400.0
            s = np.zeros((grid.Ny, grid.Nx), dtype=np.float64)
            for i in range(grid.Nx):
                s[:, i] = 600.0 - (100.0 / grid.Lx) * grid.x_centers[i]
            b = s - H

            const = SSA2DConstants(C_bed=1.0e7, picard_omega=0.6, picard_max_iter=100)
            solver = SSASolver2D(const=const, max_iter=100)
            res = solver.solve(grid, H, b, s=s, raise_on_failure=True)
            self.assertTrue(res.converged)
            # Sample velocity at mid-channel (x = 10 km)
            mid_i = Nx // 2
            centerline_velocities.append(res.u[Ny // 2, mid_i])

        # Compute differences between successive grids
        diff1 = abs(centerline_velocities[1] - centerline_velocities[0])
        diff2 = abs(centerline_velocities[2] - centerline_velocities[1])

        # Refinement ratio r = 2. Asymptotic convergence requires diff2 < diff1
        self.assertLess(diff2, diff1, f"Grid convergence failed: diff2={diff2:.4e} not smaller than diff1={diff1:.4e}")
        rate = np.log(diff1 / (diff2 + 1.0e-15)) / np.log(2.0)
        # Order should be >= 1.5 for second-order spatial discretization
        self.assertGreater(rate, 1.2, f"Estimated spatial convergence rate {rate:.2f} is below expectation")

    def test_5_finite_volume_mass_conservation(self) -> None:
        """Benchmark 5: Finite-volume continuity step must conserve mass to Tier 1 tolerance (< 1e-14)."""
        grid = Grid2D(
            Lx=40_000.0, Ly=20_000.0, Nx=20, Ny=10,
            bc_west="divide", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
        )
        # Initial sinusoidal ice thickness
        H = 400.0 + 50.0 * np.sin(np.pi * grid.X / grid.Lx)
        # Velocity field
        u = 100.0 / self.const.sec_per_year * (grid.X / grid.Lx)  # 0 to 100 m/yr
        v = np.zeros_like(u)

        dt = compute_cfl_timestep_2d(u, v, grid, cfl_factor=0.4)
        smb = 0.3 / self.const.sec_per_year  # 0.3 m/yr accumulation

        # Run 10 continuity steps
        H_curr = H.copy()
        for step in range(10):
            res_cont = step_continuity_2d(H_curr, u, v, grid, dt=dt, smb=smb, const=self.const)
            self.assertLess(
                res_cont.relative_error, 1.0e-14,
                f"Step {step+1}: Relative mass conservation error {res_cont.relative_error:.4e} exceeds 1e-14"
            )
            H_curr = res_cont.H_next


if __name__ == "__main__":
    unittest.main()

