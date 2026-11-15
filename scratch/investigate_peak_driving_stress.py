import os, sys
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import netCDF4 as nc
import pyproj

ALIGNED_NC = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
ds = nc.Dataset(ALIGNED_NC)
x_coords = ds.variables["x"][:]
y_coords = ds.variables["y"][:]
bm_m = ds.variables["mask"][:]
bm_t = ds.variables["thickness"][:]
bm_s = ds.variables["surface"][:]
bm_b = ds.variables["bed"][:]
bm_f = ds.variables["firn"][:]
bm_err = ds.variables["errbed"][:]

r0, c0 = 1774, 721

print(f"Investigating neighborhood of Row {r0}, Col {c0}:")
patch_r = range(r0 - 3, r0 + 4)
patch_c = range(c0 - 3, c0 + 4)

print("\nSurface Elevation s [m]:")
for r in patch_r:
    row_str = " ".join(f"{bm_s[r, c]:7.1f}" for c in patch_c)
    print(f"Row {r:4d}: {row_str}")

print("\nBed Elevation b [m]:")
for r in patch_r:
    row_str = " ".join(f"{bm_b[r, c]:7.1f}" for c in patch_c)
    print(f"Row {r:4d}: {row_str}")

print("\nSolid Thickness H [m]:")
for r in patch_r:
    row_str = " ".join(f"{bm_t[r, c]:7.1f}" for c in patch_c)
    print(f"Row {r:4d}: {row_str}")

print("\nMask (0=ocean, 1=rock, 2=grounded, 3=shelf):")
for r in patch_r:
    row_str = " ".join(f"{int(bm_m[r, c]):7d}" for c in patch_c)
    print(f"Row {r:4d}: {row_str}")

print("\nBed Uncertainty errbed [m]:")
for r in patch_r:
    row_str = " ".join(f"{bm_err[r, c]:7.1f}" for c in patch_c)
    print(f"Row {r:4d}: {row_str}")

# Compute gradient across row 1774 (along columns, X-direction)
# ds/dx at (1774, c) = (s[1774, c+1] - s[1774, c-1]) / (2 * 500)
for c in patch_c:
    ds_dx = (bm_s[r0, c+1] - bm_s[r0, c-1]) / 1000.0
    ds_dy = (bm_s[r0+1, c] - bm_s[r0-1, c]) / 1000.0
    grad = np.sqrt(ds_dx**2 + ds_dy**2)
    tau = 917.0 * 9.81 * bm_t[r0, c] * grad / 1000.0
    print(f"Col {c:4d} (X={x_coords[c]/1e3:,.1f} km): s={bm_s[r0, c]:.1f}m, H={bm_t[r0, c]:.1f}m, ds/dx={ds_dx:.4f}, ds/dy={ds_dy:.4f}, |grad s|={grad:.4f} ({np.degrees(np.arctan(grad)):.1f} deg), tau_d={tau:.1f} kPa")

