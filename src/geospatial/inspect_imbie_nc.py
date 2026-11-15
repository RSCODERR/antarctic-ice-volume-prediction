import xarray as xr
import os

nc_path = "antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations_1km.nc"
if os.path.exists(nc_path):
    ds = xr.open_dataset(nc_path)
    print("IMBIE 1km NetCDF summary:")
    print(ds)
    print("\nData variables:")
    for v in ds.data_vars:
        print(f"  {v}: {ds[v].attrs}")
    print("\nCoordinates:")
    for c in ds.coords:
        print(f"  {c}: shape={ds[c].shape}, min={float(ds[c].min())}, max={float(ds[c].max())}")

