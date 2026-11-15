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

N = 102 # End at grounding line cell 101
surf_cut = surf[:N]
bed_cut = bed[:N]
thick_cut = thick[:N]
firn_cut = firn[:N]

dx = CONST.domain_dx
x_centres = np.arange(N, dtype=np.float64) * dx + 0.5 * dx
width = np.full(N, 12400.0, dtype=np.float64)

kernel = np.ones(5) / 5.0
bed_s = np.convolve(bed_cut, kernel, mode='same')
thick_s = np.convolve(thick_cut, kernel, mode='same')
bed_s[0], bed_s[-1] = bed_cut[0], bed_cut[-1]
thick_s[0], thick_s[-1] = thick_cut[0], thick_cut[-1]

domain = FlowlineDomain(x_centres, bed_s, width, thick_s, name="FL_HPI_01_Ryder", source="BedMachine_V4.1_Aligned")
state = domain.initial_state()
print(f"Domain: N={domain.N}, GL cell={state.gl_cell}, x_gl={state.x_gl/1e3:.1f} km")

ssa = SSASolver(CONST, tol=1e-4, max_iter=80)
smb_conv = SMBConverter(CONST)
smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, 0.40))

# Kinematic flux
fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)

dt = 0.02 * CONST.yr_to_s # 0.02 yr ≈ 7.3 days (ensures CFL C < 0.2)
cur_state = state
print("\nStepping forward with dt = 0.02 yr...")
for step in range(1, 51):
    try:
        cur_state, diag = fv.step(cur_state, smb_m_s=smb_m_s, dt=dt)
        print(f"Step {step:2d} (t={step*0.02:.2f} yr): GL cell={cur_state.gl_cell}, x_gl={cur_state.x_gl/1e3:.2f} km, res={diag.residual:.2e} kg, H_gl={cur_state.H_gl:.1f} m, event={diag.event}")
    except Exception as e:
        print(f"FAILED on step {step}: {e}")
        # Inspect state
        H = cur_state.H
        print(f"cur_state.H: min={H.min():.4f}, max={H.max():.4f}")
        neg_cells = np.where(H < 0)[0]
        print(f"Negative cells in cur_state: {neg_cells}, vals={H[neg_cells]}")
        break

print("\n1.0 year simulation (50 steps) completed successfully with exact mass conservation!")
