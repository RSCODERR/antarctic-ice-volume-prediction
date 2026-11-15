import os, json
import netCDF4 as nc

if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

bm_nc = 'data/raw/bedmachine/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc'
print(f"Checking BedMachine: {bm_nc}")
if os.path.exists(bm_nc):
    ds = nc.Dataset(bm_nc)
    print("BedMachine Variables:", list(ds.variables.keys()))
    print("Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
    print("Mapping / CRS info:")
    for var in ['mapping', 'x', 'y']:
        if var in ds.variables:
            print(f"  {var}: {ds.variables[var].ncattrs()}")
    ds.close()
else:
    print("BedMachine NC not found!")

# Check processed BedMachine peninsula 500m
bm_proc = 'data/processed/bedmachine_v4.1_peninsula_500m.nc'
print(f"\nChecking Processed BedMachine Peninsula: {bm_proc}")
if os.path.exists(bm_proc):
    ds = nc.Dataset(bm_proc)
    print("Variables:", list(ds.variables.keys()))
    print("Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
    ds.close()

