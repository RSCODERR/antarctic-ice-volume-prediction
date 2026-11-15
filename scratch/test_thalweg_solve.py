import numpy as np
import sys
import os

sys.path.insert(0, '.')
sys.path.insert(0, 'src')
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter

from scratch.test_thalweg import bed, thick, firn, N_total

# Use the extracted thalweg profile for Ryder
dx = CONST.domain_dx
x_centres = np.arange(N_total, dtype=np.float64) * dx + 0.5 * dx
width = np.full(N_total, 12400.0, dtype=np.float64) # 12.4 km gate width from flux gate inventory

# Smooth bed to filter single-cell 500m DEM stairs (preserving macro-relief)
kernel = np.ones(5) / 5.0
bed_s = np.convolve(bed, kernel, mode='same')
thick_s = np.convolve(thick, kernel, mode='same')

domain = FlowlineDomain(x_centres, bed_s, width, thick_s, name="FL_HPI_01_Ryder", source="BedMachine_V4.1_Aligned")
state = domain.initial_state()

print(f"Domain: {domain}")
print(f"GL cell: {state.gl_cell} / {domain.N}, x_gl = {state.x_gl/1e3:.1f} km, M_gr = {state.compute_grounded_mass_kg():.3e} kg")

# Solve SSA
ssa = SSASolver(CONST, tol=1e-4, max_iter=80)
diag_ssa = ssa.solve(state)
u_m_yr = diag_ssa.u * CONST.yr_to_s
print(f"SSA solve: converged={diag_ssa.converged}, iters={diag_ssa.n_iter}, residual={diag_ssa.residual:.2e}")
print(f"Diagnostic velocity: min={np.nanmin(u_m_yr):.1f} m/yr, max={np.nanmax(u_m_yr):.1f} m/yr, GL={u_m_yr[state.gl_cell]:.1f} m/yr")

# Step FV continuity
dt = 0.05 * CONST.yr_to_s
smb_conv = SMBConverter(CONST)
smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, 0.40))
fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)

state_new, diag_step = fv.step(state, smb_m_s=smb_m_s, dt=dt)
print(f"Continuity step: dt={dt/CONST.yr_to_s:.3f} yr, residual={diag_step.residual:.2e} kg, event={diag_step.event}")
print(f"Relative mass conservation error: {abs(diag_step.residual)/state.compute_grounded_mass_kg():.2e}")
print("SUCCESS!")
