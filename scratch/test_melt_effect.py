import sys, os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))
import numpy as np
from src.physics.ssa_2d.constants import CONST_MISMIP
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d
from src.physics.ssa_2d.mismip_plus import create_mismip_bed, compute_mismip_melt_rate, find_grounding_line_x

Lx, Ly, Nx, Ny = 640_000.0, 80_000.0, 64, 9
grid = Grid2D(Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, bc_west="divide", bc_east="calving_front")
bed = create_mismip_bed(grid)
H = np.maximum(100.0, 1600.0 * (1.0 - 0.7 * (grid.X / Lx)**0.7))
solver = SSASolver2D(const=CONST_MISMIP, omega=0.5, max_iter=80, tol_rel_residual=1e-5, tol_vel_step=0.5)

f_gr, s, _ = compute_flotation_fraction_and_surface(H, bed, CONST_MISMIP)
res0 = solver.solve(grid, H, bed, s=s)

dt_sec = 5.0 * CONST_MISMIP.sec_per_year
smb_si = 0.3 / CONST_MISMIP.sec_per_year
m_shelf_si = compute_mismip_melt_rate(H, bed, f_gr, CONST_MISMIP)

# Control step (no melt)
res_ctrl = step_continuity_2d(H, res0.u, res0.v, grid, dt=dt_sec, smb=smb_si, m_shelf=0.0, const=CONST_MISMIP)
f_gr_ctrl, _, _ = compute_flotation_fraction_and_surface(res_ctrl.H_next, bed, CONST_MISMIP)
x_gl_ctrl = find_grounding_line_x(f_gr_ctrl, grid)

# Melt step
res_melt = step_continuity_2d(H, res0.u, res0.v, grid, dt=dt_sec, smb=smb_si, m_shelf=m_shelf_si, const=CONST_MISMIP)
f_gr_melt, _, _ = compute_flotation_fraction_and_surface(res_melt.H_next, bed, CONST_MISMIP)
x_gl_melt = find_grounding_line_x(f_gr_melt, grid)

print(f"x_GL control: {x_gl_ctrl/1000.0:.2f} km")
print(f"x_GL melt:    {x_gl_melt/1000.0:.2f} km")
print(f"Retreat relative to control: {(x_gl_ctrl - x_gl_melt)/1000.0:.2f} km")

