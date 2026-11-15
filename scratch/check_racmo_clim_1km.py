import netCDF4 as nc

p = "antarctic-ice-volume-prediction/data/processed/stage4_5_2/racmo2.3p2_ant055_peninsula_smb_climatology_1km.nc"
ds = nc.Dataset(p)
print("Variables in stage 4.5.2 racmo climatology:")
for k in ds.variables.keys():
    v = ds.variables[k]
    print(f"  {k}: shape={v.shape}, dtype={v.dtype}, units={getattr(v, 'units', 'None')}")
ds.close()
