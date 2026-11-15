import numpy as np
import netCDF4 as nc
import os
import sys

sys.path.insert(0, os.path.abspath('src'))
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

# Ryder Glacier trunk trace
r_start, c_start = 2250, 1700
r_end, c_end = 2436, 1585
N = 180

rows = np.round(np.linspace(r_start, r_end, N)).astype(int)
cols = np.round(np.linspace(c_start, c_end, N)).astype(int)

r_min, r_max = rows.min(), rows.max()
c_min, c_max = cols.min(), cols.max()

sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]
sub_firn = ds.variables['firn'][r_min:r_max+1, c_min:c_max+1]

thick = sub_thick[rows - r_min, cols - c_min].astype(np.float64)
bed = sub_bed[rows - r_min, cols - c_min].astype(np.float64)
mask = sub_mask[rows - r_min, cols - c_min].astype(np.int32)
firn = sub_firn[rows - r_min, cols - c_min].astype(np.float64)
ds.close()

# Mild 5-point smoothing of raw 500m DEM stairs
kernel = np.ones(5) / 5.0
bed_s = np.convolve(bed, kernel, mode='same')
thick_s = np.convolve(thick, kernel, mode='same')
thick_s = np.maximum(thick_s, 20.0) # ice thickness floor

x_centres = np.arange(N, dtype=np.float64) * CONST.domain_dx + 0.5 * CONST.domain_dx
width = np.full(N, 15000.0, dtype=np.float64)

if __name__ == '__main__':
    domain = FlowlineDomain(x_centres, bed_s, width, thick_s, name="FL_HPI_01_Ryder", source="BedMachine_V4.1_Aligned")
    state = domain.initial_state()
    print(f"Domain initialized: {domain}")
    print(f"GL cell: {state.gl_cell} / {N}, x_gl = {state.x_gl/1e3:.1f} km, grounded mass = {state.compute_grounded_mass_kg():.3e} kg")

    # SSA solve
    ssa = SSASolver(CONST, tol=1e-5, max_iter=60)
    diag_ssa = ssa.solve(state)
    u_m_yr = diag_ssa.u * CONST.yr_to_s
    print(f"SSA solve: converged={diag_ssa.converged}, iters={diag_ssa.n_iter}, residual={diag_ssa.residual:.2e}")
    print(f"Sliding velocity [m/yr]: min={np.nanmin(u_m_yr):.3f}, max={np.nanmax(u_m_yr):.3f}, GL={u_m_yr[state.gl_cell]:.3f}")

    # FV continuity with kinematic flux
    dt = 0.05 * CONST.yr_to_s
    smb_conv = SMBConverter(CONST)
    smb_m_s = smb_conv.from_m_ice_yr(np.full(N, 0.45))
    fv_kin = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)

    state_new, diag_step = fv_kin.step(state, smb_m_s=smb_m_s, dt=dt)
    print(f"Kinematic step: dt={dt/CONST.yr_to_s:.3f} yr, residual={diag_step.residual:.2e} kg, event={diag_step.event}")
    print(f"Relative mass conservation residual: {abs(diag_step.residual)/state.compute_grounded_mass_kg():.2e}")

    # FV continuity with Schoof flux
    fv_sch = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=True)
    state_new_sch, diag_step_sch = fv_sch.step(state, smb_m_s=smb_m_s, dt=dt)
    print(f"Schoof step: dt={dt/CONST.yr_to_s:.3f} yr, residual={diag_step_sch.residual:.2e} kg, event={diag_step_sch.event}")
    print(f"Relative mass conservation residual: {abs(diag_step_sch.residual)/state.compute_grounded_mass_kg():.2e}")
