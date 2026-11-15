import zipfile
import netCDF4 as nc
import tempfile
import os

zip_path = 'antarctic-ice-volume-prediction/data/raw/ismip6/ComputedScalarsPaper.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        if 'computed_iareagr_' in name and 'ctrl_proj_std' in name and 'UCIJPL' in name:
            with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
                tmp.write(z.read(name))
                tmp_path = tmp.name
            ds = nc.Dataset(tmp_path, 'r')
            print('File:', name)
            for v in ds.variables:
                if 'sector' in v or 'region' in v:
                    val0 = ds.variables[v][0] if len(ds.variables[v].shape) > 0 else ds.variables[v][:]
                    long_name = getattr(ds.variables[v], 'long_name', '')
                    print(f'{v:20s}: val[0]={val0/1e6:.1f} km2, long_name="{long_name}"')
            ds.close()
            os.remove(tmp_path)
            break
