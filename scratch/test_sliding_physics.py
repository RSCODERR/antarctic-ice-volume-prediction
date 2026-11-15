import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter

# Test with synthetic ramp:
# N=50, H=500m, slope=-0.005, width=15km
dx = 500.0
N = 50
x = np.arange(N) * dx + 0.5 * dx
bed = 500.0 - 0.005 * x
H = np.full(N, 500.0)
width = np.full(N, 15000.0)

domain = FlowlineDomain(x, bed, width, H, name="ramp_test", source="test")
state = domain.initial_state()

ssa = SSASolver(CONST, tol=1e-5, max_iter=60)
diag = ssa.solve(state)
u_yr = diag.u * CONST.s_to_yr
tau_d = CONST.rho_ice * CONST.g * H * 0.005
print(f"Ramp slope=-0.005, H=500m: tau_d = {tau_d[0]:.1f} Pa ({tau_d[0]/1e3:.1f} kPa)")
print(f"SSA converged={diag.converged}, iters={diag.n_iter}, residual={diag.residual:.2e}")
print(f"Velocity along ramp: min={u_yr.min():.4f} m/yr, max={u_yr.max():.4f} m/yr, mean={u_yr.mean():.4f} m/yr")

# Now what if C_bed is 5e5 (marine ice stream trough)?
ssa_fast = SSASolver(CONST, tol=1e-5, max_iter=60)
ssa_fast.basal.C_bed = 5e5
diag_fast = ssa_fast.solve(state)
u_yr_fast = diag_fast.u * CONST.s_to_yr
print(f"With C_bed=5e5 (soft bed): min={u_yr_fast.min():.1f} m/yr, max={u_yr_fast.max():.1f} m/yr")

