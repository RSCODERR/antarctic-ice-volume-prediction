"""
Test streaming / cropping ITS_LIVE from S3 without full 7.8 GB download.
"""
import xarray as xr
import s3fs

fs = s3fs.S3FileSystem(anon=True)
s3_path = "s3://its-live-data/velocity_mosaic/v2/annual/ITS_LIVE_velocity_120m_RGI19A_2015_v02.nc"

print("Opening ITS_LIVE via s3fs...")
try:
    with fs.open(s3_path, 'rb') as f:
        ds = xr.open_dataset(f, engine='h5netcdf')
        print("Success! Dataset coordinates and variables:")
        print(ds)
        print("x extent:", ds.x.values.min(), ds.x.values.max())
        print("y extent:", ds.y.values.min(), ds.y.values.max())
        
        # Domain A bounds in EPSG:3031
        # Peninsula: x in [-2700000, -1400000], y in [250000, 1950000]
        subset = ds.sel(x=slice(-2700000, -1400000), y=slice(1950000, 250000))
        print("Subset dimensions:", subset.dims)
        os_dest = "data/raw/its_live/ITS_LIVE_velocity_120m_Peninsula_2015_v02.nc"
        import os
        os.makedirs("data/raw/its_live", exist_ok=True)
        subset.to_netcdf(os_dest)
        print(f"Saved cropped ITS_LIVE Peninsula mosaic to {os_dest} ({os.path.getsize(os_dest)/(1024*1024):.2f} MB)")
except Exception as e:
    print(f"Streaming crop failed: {e}")

