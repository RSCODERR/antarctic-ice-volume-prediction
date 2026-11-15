import netCDF4 as nc
import numpy as np
import datetime

p = "antarctic-ice-volume-prediction/data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc"
ds = nc.Dataset(p)
times = ds.variables["time"][:]
base = datetime.datetime(1950, 1, 1)

dates = [base + datetime.timedelta(days=float(t)) for t in times]
print(f"ERAINx Start Date: {dates[0].strftime('%Y-%m-%d')}, End Date: {dates[-1].strftime('%Y-%m-%d')}")
print(f"Total Months: {len(dates)}")

# Check years with complete 12 months
from collections import Counter
year_counts = Counter([d.year for d in dates])
complete_years = [y for y, c in sorted(year_counts.items()) if c == 12]
incomplete_years = [y for y, c in sorted(year_counts.items()) if c != 12]
print(f"Complete 12-month years: {complete_years[0]} to {complete_years[-1]} (Count: {len(complete_years)})")
print(f"Incomplete years: {[(y, year_counts[y]) for y in incomplete_years]}")

ds.close()
