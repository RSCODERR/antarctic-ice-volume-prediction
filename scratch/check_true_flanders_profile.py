import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

pts = [
    (-2457000.0, 1305000.0), # Divide peak (s = 2017 m)
    (-2466040.2, 1305701.1), # GATE_IPP_01 (Leonardo Outlet)
    (-2478000.0, 1308000.0)  # Fjord mouth calving front into Flanders Bay
]

t_pts = np.linspace(0, 1, len(pts))
t_eval = np.linspace(0, 1, 50)
x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])

cols = np.clip(np.round((x_eval - xs[0]) / 500.0).astype(int), 0, len(xs)-1)
rows = np.clip(np.round((ys[0] - y_eval) / 500.0).astype(int), 0, len(ys)-1)

s = np.array([float(ds.variables['surface'][r, c]) for r, c in zip(rows, cols)])
b = np.array([float(ds.variables['bed'][r, c]) for r, c in zip(rows, cols)])
h = np.array([float(ds.variables['thickness'][r, c]) for r, c in zip(rows, cols)])
m = np.array([int(ds.variables['mask'][r, c]) for r, c in zip(rows, cols)])

print("Profile length:", len(s), "cells,", len(s)*0.5, "km")
print("Surface: start =", s[0], "m, end =", s[-1], "m, min =", s.min(), "m")
print("Bed: start =", b[0], "m, end =", b[-1], "m, min =", b.min(), "m")
print("Thickness: start =", h[0], "m, mean =", h.mean(), "m, max =", h.max(), "m")
print("Mask counts: grounded =", np.sum(m==2), "floating =", np.sum(m==3), "ocean =", np.sum(m==0), "rock =", np.sum(m==1))

