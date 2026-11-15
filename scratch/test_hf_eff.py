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

# Effective initial height above flotation consistent with BedMachine classification:
# Grounded cells have hf_init > 0. If H - h_flot <= 0 (1,077 pinning cells), assign small positive margin (e.g. 1.0 m)
# Floating cells have hf_init <= 0. If H - h_flot > 0 (3,874 cells), assign small negative margin (e.g. -1.0 m)
hf_init = H - h_flot
hf_eff = hf_init.copy()
hf_eff[grounded_init] = np.maximum(1.0, hf_init[grounded_init])
hf_eff[floating_init] = np.minimum(-1.0, hf_init[floating_init])

print(f"Initial grounded cells with hf_eff <= 0: {np.sum(grounded_init & (hf_eff <= 0))}")
print(f"Initial floating cells with hf_eff > 0: {np.sum(floating_init & (hf_eff > 0))}")
