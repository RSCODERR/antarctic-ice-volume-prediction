import netCDF4 as nc
import numpy as np

p = "antarctic-ice-volume-prediction/data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc"
ds = nc.Dataset(p)
smb_m = ds.variables["smb"][:480, 0, :, :] # 40 yrs, 1979-2018

# Sum to annual: (40, 294, 390)
smb_ann = smb_m.reshape(40, 12, 294, 390).sum(axis=1)

# Check annual sums for years 2010 to 2018 (indices 31 to 39)
years = list(range(1979, 2019))
for yr in range(2013, 2019):
    idx = years.index(yr)
    ann_f = smb_ann[idx]
    # mean over native domain
    print(f"Year {yr} (index {idx}): Native mean={ann_f.mean():.1f} mm w.e./yr, min={ann_f.min():.1f}, max={ann_f.max():.1f}")

clim = smb_ann.mean(axis=0)
print(f"\nClimatology (1979-2018): Native mean={clim.mean():.1f} mm w.e./yr, min={clim.min():.1f}, max={clim.max():.1f}")
ds.close()
