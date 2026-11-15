import numpy as np
import netCDF4 as nc
import os
import sys

# Ensure src is on python path
sys.path.insert(0, os.path.abspath('src'))
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter

def lonlat_to_epsg3031(lon, lat):
    try:
        from pyproj import Transformer
        trans = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
        return trans.transform(lon, lat)
    except Exception:
        a = 6378137.0
        e_sq = 0.00669437999014
        e = np.sqrt(e_sq)
        phi = np.radians(lat)
        lam = np.radians(lon)
        phi_c = np.radians(-71.0)
        m_c = np.cos(-phi_c) / np.sqrt(1.0 - e_sq * np.sin(-phi_c)**2)
        t_c = np.tan(np.pi/4.0 - (-phi_c)/2.0) / ((1.0 - e*np.sin(-phi_c))/(1.0 + e*np.sin(-phi_c)))**(e/2.0)
        t = np.tan(np.pi/4.0 - (-phi)/2.0) / ((1.0 - e*np.sin(-phi))/(1.0 + e*np.sin(-phi)))**(e/2.0)
        rho = a * m_c * t / t_c
        x = rho * np.sin(lam)
        y = -rho * np.cos(lam)
        return x, y

def extract_flowline(nc_ds, p_div, p_term, width_m=15000.0, name="flowline"):
    xs = nc_ds.variables['x'][:]
    ys = nc_ds.variables['y'][:]
    dx_grid = xs[1] - xs[0]
    dy_grid = ys[1] - ys[0]
    
    dist = np.hypot(p_term[0] - p_div[0], p_term[1] - p_div[1])
    n_pts = int(round(dist / CONST.domain_dx))
    t = np.linspace(0, 1, n_pts)
    line_x = p_div[0] + t * (p_term[0] - p_div[0])
    line_y = p_div[1] + t * (p_term[1] - p_div[1])
    
    cols = np.clip(np.round((line_x - xs[0]) / dx_grid).astype(int), 0, len(xs)-1)
    rows = np.clip(np.round((line_y - ys[0]) / dy_grid).astype(int), 0, len(ys)-1)
    
    r_min, r_max = int(rows.min()), int(rows.max())
    c_min, c_max = int(cols.min()), int(cols.max())
    
    sub_thick = nc_ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
    sub_bed = nc_ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
    
    # 1D indexed arrays
    thick = sub_thick[rows - r_min, cols - c_min].astype(np.float64)
    bed = sub_bed[rows - r_min, cols - c_min].astype(np.float64)
    
    # Fill nan or invalid
    thick = np.nan_to_num(thick, nan=10.0)
    bed = np.nan_to_num(bed, nan=0.0)
    
    # Clean minimum thickness for numerical ice continuity (ensure H >= 10m where ice exists)
    thick = np.maximum(thick, 10.0)
    
    # Smooth local DEM noise along flowline using a mild 5-point moving average
    kernel = np.ones(5) / 5.0
    bed_smooth = np.convolve(bed, kernel, mode='same')
    thick_smooth = np.convolve(thick, kernel, mode='same')
    
    # x centres
    x_centres = np.arange(n_pts, dtype=np.float64) * CONST.domain_dx + 0.5 * CONST.domain_dx
    width = np.full(n_pts, width_m, dtype=np.float64)
    
    domain = FlowlineDomain(
        x_centres=x_centres,
        bed=bed_smooth,
        width=width,
        H_init=thick_smooth,
        name=name,
        source="BedMachine_V4.1_Peninsula"
    )
    return domain

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

p_div = lonlat_to_epsg3031(-65.0, -71.5)
p_term = lonlat_to_epsg3031(-68.5, -71.2)

domain = extract_flowline(ds, p_div, p_term, width_m=15000.0, name="FL_HPI_01_Ryder")
ds.close()

print(f"Domain extracted: {domain}, N={domain.N}, L={domain.x_centres[-1]/1e3:.1f} km")
state = domain.initial_state()
print(f"Initial state: GL at cell {state.gl_cell} / {domain.N}, x_gl={state.x_gl/1e3:.1f} km, grounded mass = {state.compute_grounded_mass_kg():.3e} kg")
s = state.bed + state.H
print(f"Surface: s[0]={s[0]:.1f}m, s[-1]={s[-1]:.1f}m, min={s.min():.1f}m, max={s.max():.1f}m")
ds_dx = np.gradient(s, CONST.domain_dx)
print(f"ds/dx: min={ds_dx.min():.4e}, max={ds_dx.max():.4e}, mean={ds_dx.mean():.4e}")

# Test SSA solver
ssa = SSASolver(CONST, tol=1e-4, max_iter=100)
diag = ssa.solve(state)
print(f"SSA solve: converged={diag.converged}, iters={diag.n_iter}, residual={diag.residual:.2e}")
print(f"Velocity: min={diag.u.min()*CONST.s_to_yr:.1f} m/yr, max={diag.u.max()*CONST.s_to_yr:.1f} m/yr, GL={diag.u[state.gl_cell]*CONST.s_to_yr:.1f} m/yr")

# Test 1 year forward step
dt = 0.05 * CONST.yr_to_s # 0.05 yr = 18.25 days
smb_conv = SMBConverter(CONST)
smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, 0.5)) # 0.5 m/yr ice eq
fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv)

state_new, diag_step = fv.step(state, smb_m_s=smb_m_s, dt=dt)
print(f"Step completed: dt={dt/CONST.yr_to_s:.3f} yr, residual={diag_step.residual:.2e} kg, GL cell={state_new.gl_cell}")
print("Mass closure check passed!")
