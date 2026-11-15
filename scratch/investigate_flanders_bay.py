import numpy as np
import sys
import os
import netCDF4 as nc

sys.path.insert(0, '.')
sys.path.insert(0, 'src')
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.basal_drag import BasalDrag
from physics.lateral_drag import LateralDrag

# Load Flanders Bay domain as extracted in Stage 2
from scratch.extract_all_observational_flowlines import extracted_data

fl_data = extracted_data["FL_IIPP_01"]
cfg = fl_data["cfg"]
print(f"=== FLANDERS BAY GLACIER CONFIG ===")
print("Name:", cfg["name"])
print("Basin:", cfg["basin"])
print("Waypoints:", cfg["waypoints"])
print("Width:", cfg["width_m"], "m")
print("Reported Obs GL Velocity:", cfg["obs_velocity_gl"], "m/yr")

# Recreate Stage 2 Flanders domain exactly as run in run_stage2_observational_diagnostics.py
thick_raw = fl_data["thick"]
bed_raw = fl_data["bed"]
surf_raw = fl_data["surf"]
firn_raw = fl_data["firn"]

from scipy.ndimage import gaussian_filter1d
peak_idx = int(np.argmax(surf_raw[:10]))
term_idx = int(np.argmin(surf_raw))
if term_idx <= peak_idx:
    term_idx = len(surf_raw) - 1

thick_cut = thick_raw[peak_idx:term_idx+1].copy()
bed_cut = bed_raw[peak_idx:term_idx+1].copy()
surf_cut = surf_raw[peak_idx:term_idx+1].copy()

sigma_cells = 3.0
bed_s = gaussian_filter1d(bed_cut, sigma=sigma_cells, mode='nearest')
thick_s = gaussian_filter1d(thick_cut, sigma=sigma_cells, mode='nearest')
thick_s = np.maximum(thick_s, 50.0)

N_actual = len(thick_s)
x_centres = np.arange(N_actual, dtype=np.float64) * CONST.domain_dx + 0.5 * CONST.domain_dx
width = np.full(N_actual, cfg["width_m"], dtype=np.float64)

domain = FlowlineDomain(x_centres, bed_s, width, thick_s, name="FL_IIPP_01", source="Stage2")
state = domain.initial_state()

print(f"\nDomain: N={domain.N}, Length={domain.x_centres[-1]/1e3:.2f} km")
print(f"GL cell: {state.gl_cell}, x_gl={state.x_gl/1e3:.2f} km")
print(f"Thickness: min={state.H.min():.1f}m, mean={state.H.mean():.1f}m, max={state.H.max():.1f}m, at GL={state.H_gl:.1f}m")
print(f"Bed: min={state.bed.min():.1f}m, mean={state.bed.mean():.1f}m, max={state.bed.max():.1f}m, at GL={state.bed[state.gl_cell]:.1f}m")
surf_eval = state.bed + state.H
print(f"Surface: min={surf_eval.min():.1f}m, max={surf_eval.max():.1f}m, drop={surf_eval[0] - surf_eval[-1]:.1f}m over {domain.x_centres[-1]/1e3:.1f} km")

ds_dx = np.gradient(surf_eval, CONST.domain_dx)
tau_d = np.maximum(0.0, -ds_dx) * CONST.rho_ice * CONST.g * state.H
print(f"Surface slope ds/dx: min={ds_dx.min():.4f}, mean={ds_dx.mean():.4f}, max={ds_dx.max():.4f}")
print(f"Mean -ds/dx (downhill slope): {-ds_dx.mean():.4f} ({ -ds_dx.mean()*100:.1f}%)")
print(f"Driving stress tau_d: min={tau_d.min():.1f} Pa, mean={tau_d.mean():.1f} Pa, max={tau_d.max():.1f} Pa")

# Run SSA solve with detailed diagnostics
ssa = SSASolver(CONST, tol=1e-4, max_iter=80)
diag = ssa.solve(state, u_upstream=0.0)
u_m_s = diag.u
u_m_yr = u_m_s * CONST.yr_to_s

print(f"\nSSA Solve Results:")
print(f"  Converged: {diag.converged}, Iterations: {diag.n_iter}, Residual: {diag.residual:.2e}")
print(f"  Simulated GL Velocity: {u_m_yr[state.gl_cell]:.1f} m/yr")
print(f"  Simulated Mean Velocity: {np.nanmean(u_m_yr):.1f} m/yr")
print(f"  Simulated Max Velocity: {np.nanmax(u_m_yr):.1f} m/yr")

# Breakdown of stresses at each cell
print("\nCell-by-cell Stress Breakdown:")
print("cell | x [km] | H [m] | z_b [m] | s [m] | ds/dx  | tau_d [kPa] | u [m/yr] | tau_b [kPa] | tau_lat [kPa]")
print("-" * 95)

basal = BasalDrag(CONST)
lateral = LateralDrag(CONST)
tau_b = basal.tau_b(u_m_s)
tau_lat = lateral.lateral_body_force(u_m_s, width)

for i in range(domain.N):
    print(f"{i:4d} | {x_centres[i]/1e3:6.2f} | {state.H[i]:5.1f} | {state.bed[i]:7.1f} | {surf_eval[i]:6.1f} | {ds_dx[i]:6.3f} | {tau_d[i]/1e3:11.1f} | {u_m_yr[i]:8.1f} | {tau_b[i]/1e3:11.1f} | {tau_lat[i]/1e3:13.1f}")
