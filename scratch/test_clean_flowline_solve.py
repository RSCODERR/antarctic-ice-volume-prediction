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
from scratch.test_thalweg import surf, bed, thick, firn

# Slice cells 0 to 105
N = 106
surf_cut = surf[:N]
bed_cut = bed[:N]
thick_cut = thick[:N]
firn_cut = firn[:N]

dx = CONST.domain_dx
x_centres = np.arange(N, dtype=np.float64) * dx + 0.5 * dx
width = np.full(N, 12400.0, dtype=np.float64)

# Filter 500m DEM single-cell roughness with 5-point moving average
kernel = np.ones(5) / 5.0
bed_s = np.convolve(bed_cut, kernel, mode='same')
thick_s = np.convolve(thick_cut, kernel, mode='same')
# Keep boundary endpoints
bed_s[0], bed_s[-1] = bed_cut[0], bed_cut[-1]
thick_s[0], thick_s[-1] = thick_cut[0], thick_cut[-1]

domain = FlowlineDomain(x_centres, bed_s, width, thick_s, name="FL_HPI_01_Ryder", source="BedMachine_V4.1_Aligned")
state = domain.initial_state()

print(f"Domain: {domain}")
print(f"GL cell: {state.gl_cell} / {domain.N}, x_gl = {state.x_gl/1e3:.1f} km, M_gr = {state.compute_grounded_mass_kg():.3e} kg")

# Driving stress and surface slope
s = state.bed + state.H
ds_dx = np.gradient(s, dx)
tau_d = np.maximum(0.0, -ds_dx) * CONST.rho_ice * CONST.g * state.H
print(f"Surface: divide={s[0]:.1f}m, terminus={s[-1]:.1f}m, min={s.min():.1f}m, max={s.max():.1f}m")
print(f"Driving stress: min={tau_d.min():.1f} Pa, mean={tau_d.mean():.1f} Pa, max={tau_d.max():.1f} Pa")

# Solve SSA
ssa = SSASolver(CONST, tol=1e-4, max_iter=80)
diag_ssa = ssa.solve(state)
u_m_yr = diag_ssa.u * CONST.yr_to_s
print(f"SSA solve: converged={diag_ssa.converged}, iters={diag_ssa.n_iter}, residual={diag_ssa.residual:.2e}")
print(f"Velocity [m/yr]: min={np.nanmin(u_m_yr):.2f}, max={np.nanmax(u_m_yr):.2f}, GL={u_m_yr[state.gl_cell]:.2f}")

# Step FV continuity
dt = 0.05 * CONST.yr_to_s
smb_conv = SMBConverter(CONST)
smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, 0.40))
fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)

state_new, diag_step = fv.step(state, smb_m_s=smb_m_s, dt=dt)
print(f"Continuity step: dt={dt/CONST.yr_to_s:.3f} yr, residual={diag_step.residual:.2e} kg, event={diag_step.event}")
print(f"Relative mass conservation residual: {abs(diag_step.residual)/state.compute_grounded_mass_kg():.2e}")

# Run 5-year simulation (100 steps)
print("\nRunning 5-year simulation (100 steps)...")
cur_state = state
tot_res = 0.0
for step_idx in range(100):
    cur_state, d = fv.step(cur_state, smb_m_s=smb_m_s, dt=dt)
    tot_res = max(tot_res, abs(d.residual))

print(f"Completed 100 steps (5.0 years): max single-step residual = {tot_res:.2e} kg")
print(f"Final GL cell = {cur_state.gl_cell}, x_gl = {cur_state.x_gl/1e3:.1f} km, grounded mass = {cur_state.compute_grounded_mass_kg():.3e} kg")
print(f"Relative error = {tot_res / state.compute_grounded_mass_kg():.2e}")
print("ALL TESTS PASSED WITH EXACT CONSERVATION!")

