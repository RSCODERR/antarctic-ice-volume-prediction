import netCDF4 as nc
import os
import numpy as np

racmo_dir = "antarctic-ice-volume-prediction/data/raw/racmo"
files = os.listdir(racmo_dir)
print("Files in raw racmo:")
for f in files:
    if f.endswith(".nc"):
        p = os.path.join(racmo_dir, f)
        ds = nc.Dataset(p)
        print(f"\n--- {f} ---")
        print("Dimensions:", {d: len(ds.dimensions[d]) for d in ds.dimensions})
        print("Variables:", list(ds.variables.keys()))
        for v in ["time", "smb", "smb_yearly", "lat", "lon", "x", "y", "rotated_pole"]:
            if v in ds.variables:
                var = ds.variables[v]
                print(f"  {v}: shape={var.shape}, dtype={var.dtype}, units={getattr(var, 'units', 'None')}")
        if "time" in ds.variables:
            t_var = ds.variables["time"]
            print(f"  time min={t_var[0]}, max={t_var[-1]}, count={len(t_var)}")
        ds.close()
