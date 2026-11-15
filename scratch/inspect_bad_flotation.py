import netCDF4 as nc
import numpy as np

NC_UNIFIED = "data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
ds = nc.Dataset(NC_UNIFIED)
H = ds.variables["thickness"][:].astype(np.float64)
bed = ds.variables["bed"][:].astype(np.float64)
ag = ds.variables["alpha_grounded"][:].astype(np.float64)
af = ds.variables["alpha_floating"][:].astype(np.float64)
ds.close()

RHO_ICE = 917.0
RHO_WATER = 1028.0
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)
hf = H - h_flot

flt = (af > ag) & (af > 0) & (H > 10.0)
grd = (ag >= af) & (ag > 0) & (H > 10.0)

print(f"Total floating cells: {np.sum(flt):,}")
print(f"Total grounded cells: {np.sum(grd):,}")

bad_flt = flt & (hf > 0)
print(f"Floating cells with hf > 0: {np.sum(bad_flt):,}")
print(f"  bed range on bad_flt: min={bed[bad_flt].min():.1f}, max={bed[bad_flt].max():.1f}")
print(f"  H range on bad_flt: min={H[bad_flt].min():.1f}, max={H[bad_flt].max():.1f}")
print(f"  hf range on bad_flt: min={hf[bad_flt].min():.1f}, max={hf[bad_flt].max():.1f}, median={np.median(hf[bad_flt]):.1f}")

bad_grd = grd & (hf <= 0) & (bed < 0)
print(f"Grounded cells with hf <= 0 and bed < 0: {np.sum(bad_grd):,}")
print(f"  bed range on bad_grd: min={bed[bad_grd].min():.1f}, max={bed[bad_grd].max():.1f}")
print(f"  H range on bad_grd: min={H[bad_grd].min():.1f}, max={H[bad_grd].max():.1f}")
print(f"  hf range on bad_grd: min={hf[bad_grd].min():.1f}, max={hf[bad_grd].max():.1f}, median={np.median(hf[bad_grd]):.1f}")
