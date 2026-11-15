import zipfile
import netCDF4 as nc
import tempfile
import os

zip_path = 'antarctic-ice-volume-prediction/data/raw/ismip6/ComputedScalarsPaper.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    all_names = z.namelist()
    
# Find unique variable prefixes in ComputedScalarsPaper
var_prefixes = set()
for n in all_names:
    fn = n.split('/')[-1]
    if fn.startswith('computed_') and fn.endswith('.nc'):
        # extract variable name
        parts = fn.replace('computed_', '').split('_')
        # parts could be ['icearea', ...], ['ivaf', ...], ['iareagr', ...], ['vaf', ...], etc.
        var_prefixes.add(parts[0])

print("Variable prefixes found in archive filenames:", sorted(list(var_prefixes)))

# Let's inspect NetCDF attributes for each variable type
sample_files = {}
for p in sorted(list(var_prefixes)):
    for n in all_names:
        fn = n.split('/')[-1]
        if fn.startswith(f'computed_{p}_') and 'minus_ctrl_proj' not in fn and 'ctrl_proj_std' in n:
            sample_files[p] = n
            break
    if p not in sample_files:
        for n in all_names:
            fn = n.split('/')[-1]
            if fn.startswith(f'computed_{p}_'):
                sample_files[p] = n
                break

print("\n=== SAMPLE NETCDF ATTRIBUTES ===")
with zipfile.ZipFile(zip_path, 'r') as z:
    for p, fn in sample_files.items():
        with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
            tmp.write(z.read(fn))
            tmp_path = tmp.name
        ds = nc.Dataset(tmp_path, 'r')
        print(f"\n--- Variable Prefix: {p} (File: {fn.split('/')[-1]}) ---")
        for v in ds.variables:
            if v in ['time', 'rhoi', 'rhow']: continue
            v_obj = ds.variables[v]
            attrs = {a: getattr(v_obj, a) for a in v_obj.ncattrs()}
            print(f"  Var: {v:20s} | dims={v_obj.dimensions} | shape={v_obj.shape} | attrs={attrs}")
            break # just print the first sector/region var
        ds.close()
        os.remove(tmp_path)

