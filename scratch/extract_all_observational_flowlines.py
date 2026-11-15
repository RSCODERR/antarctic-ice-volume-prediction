import numpy as np
import netCDF4 as nc
import os
import sys

sys.path.insert(0, '.')
sys.path.insert(0, 'src')
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
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

flowline_configs = {
    "FL_HPI_01": {
        "name": "Ryder / Bertram Glacier System (Palmer Land West)",
        "basin": "Hp-I",
        "waypoints": [
            (-1820000.0, 820000.0), # Divide
            (-1860000.0, 785000.0), # Mid trunk
            (-1907000.0, 745000.0)  # Terminus
        ],
        "width_m": 12400.0,
        "n_pts": 105,
        "smb_ice_yr": 0.40,
        "obs_velocity_gl": 385.0 # InSAR
    },
    "FL_IIPP_01": {
        "name": "Flanders Bay System (Graham Land West)",
        "basin": "I-Ipp",
        "waypoints": [
            (-2440000.0, 1290000.0), # Divide spine
            (-2460000.0, 1275000.0), # Fjord trunk
            (-2475000.0, 1265000.0)  # Fjord mouth
        ],
        "width_m": 3800.0,
        "n_pts": 60,
        "smb_ice_yr": 0.65,
        "obs_velocity_gl": 210.0 # InSAR
    },
    "FL_IPPJ_02": {
        "name": "Crane Glacier System (Larsen B Tributary)",
        "basin": "Ipp-J",
        "waypoints": [
            (-2455000.0, 1180000.0), # Divide plateau
            (-2435000.0, 1205000.0), # Mid canyon
            (-2420000.0, 1226000.0)  # Terminus at Larsen B
        ],
        "width_m": 6500.0,
        "n_pts": 70,
        "smb_ice_yr": 0.35,
        "obs_velocity_gl": 680.0 # Post-collapse surge InSAR
    }
}

extracted_data = {}

for fl_id, cfg in flowline_configs.items():
    pts = cfg["waypoints"]
    N_pts = cfg["n_pts"]
    t_pts = np.linspace(0, 1, len(pts))
    t_eval = np.linspace(0, 1, N_pts)
    
    x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
    y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])
    
    cols = np.clip(np.round((x_eval - xs[0]) / dx).astype(int), 0, len(xs)-1)
    rows = np.clip(np.round((y_eval - ys[0]) / dy).astype(int), 0, len(ys)-1)
    
    r_min = max(0, rows.min() - 15)
    r_max = min(len(ys)-1, rows.max() + 15)
    c_min = max(0, cols.min() - 15)
    c_max = min(len(xs)-1, cols.max() + 15)
    
    sub_surf = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
    sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
    sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
    sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]
    sub_firn = ds.variables['firn'][r_min:r_max+1, c_min:c_max+1]
    
    # Thalweg search
    thalweg_r = []
    thalweg_c = []
    for r_target, c_target in zip(rows, cols):
        r_loc = r_target - r_min
        c_loc = c_target - c_min
        r0 = max(0, r_loc - 6)
        r1 = min(sub_thick.shape[0], r_loc + 7)
        c0 = max(0, c_loc - 6)
        c1 = min(sub_thick.shape[1], c_loc + 7)
        
        w_thick = np.array(sub_thick[r0:r1, c0:c1])
        w_mask = np.array(sub_mask[r0:r1, c0:c1])
        w_thick[w_mask == 1] = -1.0
        
        max_idx = np.unravel_index(np.nanargmax(w_thick), w_thick.shape)
        thalweg_r.append(r_min + r0 + max_idx[0])
        thalweg_c.append(c_min + c0 + max_idx[1])
    
    rel_r = np.array(thalweg_r) - r_min
    rel_c = np.array(thalweg_c) - c_min
    
    thick_raw = sub_thick[rel_r, rel_c].astype(np.float64)
    bed_raw = sub_bed[rel_r, rel_c].astype(np.float64)
    surf_raw = sub_surf[rel_r, rel_c].astype(np.float64)
    mask_raw = sub_mask[rel_r, rel_c].astype(np.int32)
    firn_raw = sub_firn[rel_r, rel_c].astype(np.float64)
    
    # Smooth raw 500m DEM stairs (5-point moving average)
    kernel = np.ones(5) / 5.0
    bed_s = np.convolve(bed_raw, kernel, mode='same')
    thick_s = np.convolve(thick_raw, kernel, mode='same')
    bed_s[0], bed_s[-1] = bed_raw[0], bed_raw[-1]
    thick_s[0], thick_s[-1] = thick_raw[0], thick_raw[-1]
    
    extracted_data[fl_id] = {
        "cfg": cfg,
        "x": np.arange(N_pts, dtype=np.float64) * CONST.domain_dx + 0.5 * CONST.domain_dx,
        "bed": bed_s,
        "thick": thick_s,
        "surf": surf_raw,
        "mask": mask_raw,
        "firn": firn_raw
    }

ds.close()

print("Extracted profiles for all 3 glaciers successfully:")
for fl_id, d in extracted_data.items():
    print(f"\n{fl_id}: {d['cfg']['name']}")
    print(f"  Length: {len(d['x'])*0.5:.1f} km, Width: {d['cfg']['width_m']/1e3:.1f} km")
    print(f"  Thickness: mean={d['thick'].mean():.1f}m, max={d['thick'].max():.1f}m, min={d['thick'].min():.1f}m")
    print(f"  Bed: min={d['bed'].min():.1f}m, max={d['bed'].max():.1f}m")
    print(f"  Firn: mean={d['firn'].mean():.1f}m, max={d['firn'].max():.1f}m")

