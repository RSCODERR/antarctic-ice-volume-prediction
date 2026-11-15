import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

for y_val in [1300000.0, 1305000.0, 1310000.0, 1315000.0]:
    r = int(round((ys[0] - y_val) / 500.0))
    s_row = np.array([float(v) for v in ds.variables['surface'][r, :]])
    b_row = np.array([float(v) for v in ds.variables['bed'][r, :]])
    h_row = np.array([float(v) for v in ds.variables['thickness'][r, :]])
    m_row = np.array([int(v) for v in ds.variables['mask'][r, :]])
    
    # Peak elevation on Peninsula spine:
    peak_idx = np.argmax(s_row)
    print(f"y={y_val/1e3:.1f} km: Divide Peak at x={xs[peak_idx]/1e3:.1f} km, s={s_row[peak_idx]:.1f}m, b={b_row[peak_idx]:.1f}m, H={h_row[peak_idx]:.1f}m")
    
    # Let's see the profile from x = xs[peak_idx] westward to x = -2480 km
    c_west = int(round((-2480000 - xs[0]) / 500.0))
    c_peak = peak_idx
    step = 1 if c_west > c_peak else -1
    cols = range(c_peak, c_west, step)
    s_west = s_row[cols]
    b_west = b_row[cols]
    h_west = h_row[cols]
    m_west = m_row[cols]
    print(f"  Westward to -2480 km: s drops to {s_west[-1]:.1f}m over {abs(c_west-c_peak)*0.5:.1f} km. Min bed={b_west.min():.1f}m")

