import sys, os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))
import numpy as np
from src.physics.ssa_2d.constants import CONST_DEFAULT
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.solver import SSASolver2D

grid = Grid2D(Lx=20000, Ly=10000, Nx=8, Ny=4, bc_west="divide", bc_east="free_slip")
H = np.ones((grid.Ny, grid.Nx)) * 500.0
b = np.zeros((grid.Ny, grid.Nx))
solver = SSASolver2D(const=CONST_DEFAULT, max_iter=20)
res = solver.solve(grid, H, b, raise_on_failure=True)
print(f"Converged: {res.converged}, n_iter: {res.n_iter}, max_u: {np.max(np.abs(res.u)):.4e}")

