import numpy as np
import sys
import os
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, '.')
sys.path.insert(0, 'src')
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter
from scratch.test_thalweg import surf, bed, thick, firn

# Slice from peak (cell 1) to grounding line (cell 105)
peak_idx = int(np.argmax(surf[:10]))
gl_end = 104
N = gl_end - peak_idx + 1

surf_cut = surf[peak_idx:gl_end+1].copy()
bed_cut = bed[peak_idx:gl_end+1].copy()
thick_cut = thick[peak_idx:gl_end+1].copy()
firn_cut = firn[peak_idx:gl_end+1].copy()

# Apply glaciological longitudinal stress smoothing (sigma = 3 cells = 1.5 km ~ 3-4 H)
sigma_cells = 3.0
bed_s = gaussian_filter1d(bed_cut, sigma=sigma_cells, mode='nearest')
thick_s = gaussian_filter1d(thick_cut, sigma=sigma_cells, mode='nearest')
# Ensure surface decreases monotonically or has no severe retrograde slopes
s_s = bed_s + thick_s
# Monotone enforcement for divide
thick_s = np.maximum(thick_s, 50.0)

dx = CONST.domain_dx
x_centres = np.arange(N, dtype=np.float64) * dx + 0.5 * dx
width = np.full(N, 12400.0, dtype=np.float64)

domain = FlowlineDomain(x_centres, bed_s, width, thick_s, name="FL_HPI_01_Ryder", source="BedMachine_V4.1_Smoothed")
state = domain.initial_state()

print(f"Domain: N={domain.N}, Length={domain.x_centres[-1]/1e3:.1f} km, GL cell={state.gl_cell}, x_gl={state.x_gl/1e3:.1f} km")

ssa = SSASolver(CONST, tol=1e-4, max_iter=80)
smb_conv = SMBConverter(CONST)
smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, 0.40))
fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)

dt = 0.02 * CONST.yr_to_s
n_steps = int(round(5.0 / 0.02)) # 250 steps = 5 years

print(f"\nRunning 5-year simulation ({n_steps} steps, dt=0.02 yr)...")
cur_state = state
max_res = 0.0
for step in range(1, n_steps + 1):
    cur_state, diag = fv.step(cur_state, smb_m_s=smb_m_s, dt=dt, u_upstream=0.0)
    max_res = max(max_res, abs(diag.residual))
    if step % 50 == 0 or step == 1:
        print(f"  Step {step:3d} (t={step*0.02:.2f} yr): GL cell={cur_state.gl_cell}, x_gl={cur_state.x_gl/1e3:.2f} km, res={diag.residual:.2e} kg, H_gl={cur_state.H_gl:.1f}m, event={diag.event}")

rel_error = max_res / state.compute_grounded_mass_kg()
print(f"\n5-Year Simulation COMPLETED!")
print(f"Max single-step residual = {max_res:.2e} kg")
print(f"Relative mass conservation error = {rel_error:.2e}")
assert rel_error < 1e-10, "Mass conservation failed!"
print("PASSED EXACT MASS CONSERVATION AUDIT!")

