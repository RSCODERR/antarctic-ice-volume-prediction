import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

for x_start in [-2430000.0, -2435000.0, -2440000.0]:
    for y_start in [1295000.0, 1300000.0, 1305000.0]:
        pts = [(x_start, y_start), (-2450000.0, 1305000.0), (-2466040.2, 1305701.1)]
        t_pts = np.linspace(0, 1, len(pts))
        t_eval = np.linspace(0, 1, 40)
        x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
        y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])
        
        cols = np.clip(np.round((x_eval - xs[0]) / 500.0).astype(int), 0, len(xs)-1)
        rows = np.clip(np.round((ys[0] - y_eval) / 500.0).astype(int), 0, len(ys)-1)
        
        s = np.array([float(ds.variables['surface'][r, c]) for r, c in zip(rows, cols)])
        b = np.array([float(ds.variables['bed'][r, c]) for r, c in zip(rows, cols)])
        h = np.array([float(ds.variables['thickness'][r, c]) for r, c in zip(rows, cols)])
        m = np.array([int(ds.variables['mask'][r, c]) for r, c in zip(rows, cols)])
        
        print(f"Start ({x_start/1e3:.0f}, {y_start/1e3:.0f}): s_start={s[0]:.1f}m, s_end={s[-1]:.1f}m, drop={s[0]-s[-1]:.1f}m, mean H={h.mean():.1f}m, mean b={b.mean():.1f}m, min b={b.min():.1f}m, mask: gr={np.sum(m==2)}, oc={np.sum(m==0)}, wall={np.sum(m==1)}")
