import netCDF4 as nc
import numpy as np

NC_UNIFIED = "data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
ds = nc.Dataset(NC_UNIFIED)
H = ds.variables["thickness"][:].astype(np.float64)
bed = ds.variables["bed"][:].astype(np.float64)
ag = ds.variables["alpha_grounded"][:].astype(np.float64)
af = ds.variables["alpha_floating"][:].astype(np.float64)
area = ds.variables["cell_area_wgs84_m2"][:].astype(np.float64)
ds.close()

grounded_init = (ag >= af) & (ag > 0) & (H > 10.0)
floating_init = (af > ag) & (af > 0) & (H > 10.0)

RHO_ICE = 917.0
RHO_WATER = 1028.0
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)
hf_0 = H - h_flot

flt_with_hf_gt_0 = floating_init & (hf_0 > 0)
grd_with_hf_le_0 = grounded_init & (hf_0 <= 0) & (bed < 0)

print(f"Floating cells with hf > 0 at t=0: {np.sum(flt_with_hf_gt_0):,} cells")
print(f"Total mass of floating cells with hf > 0: {np.sum(H[flt_with_hf_gt_0] * area[flt_with_hf_gt_0]) * RHO_ICE * 1e-12:.2f} Gt")

print(f"Grounded cells with hf <= 0 at t=0: {np.sum(grd_with_hf_le_0):,} cells")
print(f"Total mass of grounded cells with hf <= 0: {np.sum(H[grd_with_hf_le_0] * area[grd_with_hf_le_0]) * RHO_ICE * 1e-12:.2f} Gt")
