import netCDF4 as nc
import numpy as np

RACMO_RAW = "data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc"
ds_r = nc.Dataset(RACMO_RAW)
time_var = ds_r.variables["time"]
print("Time units:", time_var.units)
print("Time shape:", time_var.shape)

# Let's inspect months 420 to 480 (years 2014 to 2018)
# Year 1979 has 12 months: index 0 to 11
# 2014 is year index: 2014 - 1979 = 35 -> months 35*12 = 420 to 431
# 2015 is year index: 36 -> months 432 to 443
# 2016 is year index: 37 -> months 444 to 455
# 2017 is year index: 38 -> months 456 to 467
# 2018 is year index: 39 -> months 468 to 479

smb_m = ds_r.variables["smb"][:, 0, :, :]
print("smb_m shape:", smb_m.shape)
ds_r.close()

years = [2014, 2015, 2016, 2017]
for yr in years:
    y_idx = yr - 1979
    m_start = y_idx * 12
    m_end = m_start + 12
    annual_sum = smb_m[m_start:m_end].sum(axis=0)
    print(f"Year {yr} (months {m_start}:{m_end}): min={annual_sum.min():.1f}, max={annual_sum.max():.1f}, mean={annual_sum.mean():.1f} mm w.e./yr")
