import netCDF4 as nc
import numpy as np
import scipy.ndimage

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_q = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_quality_masks.nc"

ds_u = nc.Dataset(path_u)
H = ds_u.variables["thickness"][:]
surface = ds_u.variables["surface"][:]
td = ds_u.variables["driving_stress"][:]
alpha_g = ds_u.variables["alpha_grounded"][:]
spd_0720 = ds_u.variables["speed_0720"][:]
err_0720 = ds_u.variables["error_0720"][:]
spd_0761 = ds_u.variables["speed_0761"][:]
err_0761 = ds_u.variables["error_0761"][:]
ds_u.close()

ds_q = nc.Dataset(path_q)
qm_0720 = ds_q.variables["quality_mask_nsidc0720"][:]
qm_0761 = ds_q.variables["quality_mask_nsidc0761"][:]
ds_q.close()

dx, dy = 1000.0, 1000.0
grounded_active = (alpha_g > 0) & (H > 10.0)

# Raw surface gradient
ds_dy_raw, ds_dx_raw = np.gradient(surface, -dy, dx)
slope_raw_mag = np.sqrt(ds_dx_raw**2 + ds_dy_raw**2)
slope_raw_deg = np.rad2deg(np.arctan(slope_raw_mag))

# Smoothed surface gradient (Kamb & Echelmeyer, sigma=1.0 km)
surface_smooth = scipy.ndimage.gaussian_filter(surface, sigma=1.0)
ds_dy_smooth, ds_dx_smooth = np.gradient(surface_smooth, -dy, dx)
slope_smooth_mag = np.sqrt(ds_dx_smooth**2 + ds_dy_smooth**2)
slope_smooth_deg = np.rad2deg(np.arctan(slope_smooth_mag))

# Driving stress check
td_calc = 917.0 * 9.81 * H * slope_smooth_mag / np.sqrt(1.0 + slope_smooth_mag**2)

# Cell populations
high_stress = grounded_active & (td > 500e3) # 395 cells
gated_cells = grounded_active & (td > 500e3) & (slope_smooth_mag > 0.10) # 340 cells
retained_high_stress = grounded_active & (td > 500e3) & (slope_smooth_mag <= 0.10) # 55 cells

print(f"Total grounded active cells: {np.sum(grounded_active):,}")
print(f"High stress cells (td > 500 kPa): {np.sum(high_stress):,}")
print(f"Gated cells (td > 500 kPa & |grad s_smooth| > 0.10): {np.sum(gated_cells):,}")
print(f"Retained high stress cells (td > 500 kPa & |grad s_smooth| <= 0.10): {np.sum(retained_high_stress):,}")

# Slopes in whole domain
print("\nWhole Grounded Domain:")
print(f"  Raw slope deg: min={np.min(slope_raw_deg[grounded_active]):.2f}, mean={np.mean(slope_raw_deg[grounded_active]):.2f}, median={np.median(slope_raw_deg[grounded_active]):.2f}, max={np.max(slope_raw_deg[grounded_active]):.2f}, >35 deg cells={np.sum(slope_raw_deg[grounded_active] > 35.0)}")
print(f"  Smooth slope deg: min={np.min(slope_smooth_deg[grounded_active]):.2f}, mean={np.mean(slope_smooth_deg[grounded_active]):.2f}, median={np.median(slope_smooth_deg[grounded_active]):.2f}, max={np.max(slope_smooth_deg[grounded_active]):.2f}, >35 deg cells={np.sum(slope_smooth_deg[grounded_active] > 35.0)}")

def print_stats(name, mask):
    s_raw = slope_raw_deg[mask]
    s_sm = slope_smooth_deg[mask]
    t = td[mask] / 1e3 # kPa
    h = H[mask]
    v20 = (~np.isnan(spd_0720[mask])) & (qm_0720[mask] == 1)
    v61 = (~np.isnan(spd_0761[mask])) & (np.isin(qm_0761[mask], [1, 2]))
    print(f"\n--- {name} (N = {np.sum(mask)}) ---")
    print(f"  Raw slope (deg): min={s_raw.min():.2f}, median={np.median(s_raw):.2f}, mean={s_raw.mean():.2f}, max={s_raw.max():.2f}, 90th={np.percentile(s_raw, 90):.2f}")
    print(f"  Smooth slope (deg): min={s_sm.min():.2f}, median={np.median(s_sm):.2f}, mean={s_sm.mean():.2f}, max={s_sm.max():.2f}, 90th={np.percentile(s_sm, 90):.2f}")
    print(f"  Driving stress (kPa): min={t.min():.1f}, median={np.median(t):.1f}, mean={t.mean():.1f}, max={t.max():.1f}")
    print(f"  Ice thickness (m): min={h.min():.1f}, median={np.median(h):.1f}, mean={h.mean():.1f}, max={h.max():.1f}")
    print(f"  NSIDC-0720 valid obs: {np.sum(v20)} ({np.sum(v20)/len(s_raw)*100:.1f}%)")
    print(f"  NSIDC-0761 valid obs: {np.sum(v61)} ({np.sum(v61)/len(s_raw)*100:.1f}%)")

print_stats("High-Stress Cells (395)", high_stress)
print_stats("Gated Cells (340)", gated_cells)
print_stats("Retained High-Stress Cells (55)", retained_high_stress)
