import os, sys
if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')
sys.path.insert(0, '.')
sys.path.insert(0, 'src')

import numpy as np
import netCDF4 as nc
from scipy.ndimage import gaussian_filter1d

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

configs = {
    'FL_HPI_02': {
        'name': 'Millett / Dyer Glacier (Palmer Land West)',
        'basin': 'Hp-I',
        'waypoints': [
            (-1760000.0, 780000.0), # Dyer Plateau divide
            (-1800000.0, 755000.0), # Mid trunk
            (-1840000.0, 730000.0)  # Terminus at George VI
        ],
        'width_m': 15200.0,
        'n_pts': 90,
        'obs_u_gl': 290.0,
        'obs_sigma': 18.03,
        'smb_yr': 0.45,
        'theta_buttress': 1.0
    },
    'FL_IPPJ_03': {
        'name': 'Flask Glacier (Larsen C Tributary)',
        'basin': 'Ipp-J',
        'waypoints': [
            (-2450000.0, 1150000.0), # Divide
            (-2410000.0, 1165000.0), # Mid canyon
            (-2360000.0, 1180000.0)  # Larsen C embayment
        ],
        'width_m': 7100.0,
        'n_pts': 80,
        'obs_u_gl': 310.0,
        'obs_sigma': 18.03,
        'smb_yr': 0.40,
        'theta_buttress': 1.0
    },
    'FL_IPPJ_01': {
        'name': 'Drygalski Glacier (Larsen A Tributary)',
        'basin': 'Ipp-J',
        'waypoints': [
            (-2490000.0, 1330000.0), # Divide plateau
            (-2455000.0, 1350000.0), # Mid trunk
            (-2415000.0, 1370000.0)  # Calving front at Larsen A
        ],
        'width_m': 6200.0,
        'n_pts': 75,
        'obs_u_gl': 305.0,
        'obs_sigma': 18.03,
        'smb_yr': 0.35,
        'theta_buttress': 0.0 # Unbuttressed post-1995 Larsen A collapse
    }
}

for fl_id, cfg in configs.items():
    pts = cfg['waypoints']
    N_raw = cfg['n_pts']
    t_pts = np.linspace(0, 1, len(pts))
    t_eval = np.linspace(0, 1, N_raw)
    x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
    y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])

    cols = np.clip(np.round((x_eval - xs[0]) / dx).astype(int), 0, len(xs)-1)
    rows = np.clip(np.round((ys[0] - y_eval) / abs(dy)).astype(int), 0, len(ys)-1)

    r_min = max(0, rows.min() - 15)
    r_max = min(len(ys)-1, rows.max() + 15)
    c_min = max(0, cols.min() - 15)
    c_max = min(len(xs)-1, cols.max() + 15)

    sub_surf = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
    sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
    sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
    sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]

    thalweg_r = []
    thalweg_c = []
    for r_target, c_target in zip(rows, cols):
        r_loc = r_target - r_min
        c_loc = c_target - c_min
        r0 = max(0, r_loc - 8)
        r1 = min(sub_thick.shape[0], r_loc + 9)
        c0 = max(0, c_loc - 8)
        c1 = min(sub_thick.shape[1], c_loc + 9)
        w_thick = np.array(sub_thick[r0:r1, c0:c1])
        w_mask = np.array(sub_mask[r0:r1, c0:c1])
        w_thick[w_mask == 1] = -1.0 # exclude ice-free land
        w_thick[w_mask == 0] = -1.0 # exclude open ocean
        if np.all(w_thick < 0):
            thalweg_r.append(r_target)
            thalweg_c.append(c_target)
        else:
            max_idx = np.unravel_index(np.nanargmax(w_thick), w_thick.shape)
            thalweg_r.append(r_min + r0 + max_idx[0])
            thalweg_c.append(c_min + c0 + max_idx[1])

    rel_r = np.array(thalweg_r) - r_min
    rel_c = np.array(thalweg_c) - c_min

    thick_raw = np.array([float(sub_thick[r, c]) for r, c in zip(rel_r, rel_c)])
    bed_raw = np.array([float(sub_bed[r, c]) for r, c in zip(rel_r, rel_c)])
    surf_raw = np.array([float(sub_surf[r, c]) for r, c in zip(rel_r, rel_c)])
    mask_raw = np.array([int(sub_mask[r, c]) for r, c in zip(rel_r, rel_c)])

    peak_idx = int(np.argmax(surf_raw[:15]))
    term_idx = int(np.argmin(surf_raw))
    if term_idx <= peak_idx:
        term_idx = len(surf_raw) - 1

    gl_name = cfg['name']
    print(f"{fl_id} ({gl_name}):")
    print(f"  Raw pts: {len(surf_raw)}, Peak at {peak_idx} (surf={surf_raw[peak_idx]:.1f} m), Terminus at {term_idx} (surf={surf_raw[term_idx]:.1f} m)")
    print(f"  Elevation drop: {surf_raw[peak_idx] - surf_raw[term_idx]:.1f} m (Monotonic divide-to-ocean: {surf_raw[peak_idx] > surf_raw[term_idx]})")
    print(f"  Mean thickness: {np.mean(thick_raw[peak_idx:term_idx+1]):.1f} m, Min thickness: {np.min(thick_raw[peak_idx:term_idx+1]):.1f} m")
    print(f"  Mask counts: grounded={np.sum(mask_raw[peak_idx:term_idx+1]==2)}, shelf={np.sum(mask_raw[peak_idx:term_idx+1]==3)}")
