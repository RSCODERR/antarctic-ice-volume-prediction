import os
import netCDF4 as nc
import numpy as np
import pandas as pd

NC_UNIFIED = "data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
NC_CAL = "data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(NC_UNIFIED)
print("Variables in unified:", ds_u.variables.keys())
H_init = np.nan_to_num(np.asarray(ds_u.variables["thickness"][:]), nan=0.0).astype(np.float64)
bed = np.nan_to_num(np.asarray(ds_u.variables["bed"][:]), nan=0.0).astype(np.float64)
ag = np.nan_to_num(np.asarray(ds_u.variables["alpha_grounded"][:]), nan=0.0).astype(np.float64)
af = np.nan_to_num(np.asarray(ds_u.variables["alpha_floating"][:]), nan=0.0).astype(np.float64)
area = np.nan_to_num(np.asarray(ds_u.variables["cell_area_wgs84_m2"][:]), nan=1e6).astype(np.float64)
ds_u.close()

RHO_ICE = 917.0
RHO_WATER = 1028.0
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)
grounded_init = (ag >= af) & (ag > 0) & (H_init > 10.0)
floating_init = (af > ag) & (af > 0) & (H_init > 10.0)

# Check grounding line adjacency at t=0
gl_adj = np.zeros_like(grounded_init, dtype=bool)
gl_adj[:, :-1] |= (grounded_init[:, :-1] & floating_init[:, 1:])
gl_adj[:, 1:]  |= (grounded_init[:, 1:] & floating_init[:, :-1])
gl_adj[:-1, :] |= (grounded_init[:-1, :] & floating_init[1:, :])
gl_adj[1:, :]  |= (grounded_init[1:, :] & floating_init[:-1, :])

df_pilot = pd.read_csv("reports/tables/stage5_0_historical_pilot_results.csv")
print("\nHistorical Pilot ungrounding cells per year:\n", df_pilot[["Historical_Year", "Ungrounded_Cells_Annual", "Regrounded_Cells_Annual"]])

hf_0 = H_init - h_flot
hf_grd = hf_0[grounded_init & (H_init > h_flot) & (bed < 0)]
print(f"\nTotal grounded submarine cells with H_init > h_flot: {len(hf_grd):,}")
print(f"Distribution of hf_0:")
print(f"  hf_0 < 1m: {np.sum(hf_grd < 1.0):,}")
print(f"  hf_0 < 5m: {np.sum(hf_grd < 5.0):,}")
print(f"  hf_0 < 10m: {np.sum(hf_grd < 10.0):,}")
print(f"  hf_0 < 20m: {np.sum(hf_grd < 20.0):,}")
print(f"  Median hf_0: {np.median(hf_grd):.1f} m, Mean: {np.mean(hf_grd):.1f} m")

borderline_cells = grounded_init & (H_init > h_flot) & (bed < 0) & (hf_0 < 10.0)
print(f"Borderline cells (hf_0 < 10m) that are GL-adjacent: {np.sum(borderline_cells & gl_adj):,} out of {np.sum(borderline_cells):,}")
