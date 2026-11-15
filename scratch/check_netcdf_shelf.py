import netCDF4 as nc
import numpy as np

path = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
ds = nc.Dataset(path)

alpha_f = ds.variables["alpha_floating"][:]
alpha_g = ds.variables["alpha_grounded"][:]
alpha_r = ds.variables["alpha_rock"][:]
H = ds.variables["thickness"][:]
smb = ds.variables["smb"][:] # mm w.e. / yr = kg m-2 yr-1
cell_area = ds.variables["cell_area_wgs84_m2"][:]

# Check fractional vs macro-cell integrals
print("--- Fractional Area & Volume Integrals ---")
area_g_frac = np.sum(alpha_g * cell_area) * 1e-6
vol_g_frac = np.sum(alpha_g * H * cell_area) * 1e-9
smb_g_frac = np.sum(alpha_g * smb * cell_area) * 1e-12

area_f_frac = np.sum(alpha_f * cell_area) * 1e-6
vol_f_frac = np.sum(alpha_f * H * cell_area) * 1e-9
smb_f_frac = np.sum(alpha_f * smb * cell_area) * 1e-12

print(f"Grounded (fractional alpha_g): Area = {area_g_frac:.2f} km^2, Vol = {vol_g_frac:.2f} km^3, SMB = {smb_g_frac:.4f} Gt/yr")
print(f"Floating (fractional alpha_f): Area = {area_f_frac:.2f} km^2, Vol = {vol_f_frac:.2f} km^3, SMB = {smb_f_frac:.4f} Gt/yr")

grounded_active = (alpha_g > 0) & (H > 10.0)
area_g_act = np.sum(cell_area[grounded_active]) * 1e-6
vol_g_act = np.sum(H[grounded_active] * cell_area[grounded_active]) * 1e-9
smb_g_act = np.sum(smb[grounded_active] * cell_area[grounded_active]) * 1e-12
print(f"Grounded (macro-cell active): Area = {area_g_act:.2f} km^2, Vol = {vol_g_act:.2f} km^3, SMB = {smb_g_act:.4f} Gt/yr")

print(f"\nTarget invariants: Area = 216,062.17 km^2, Vol = 140,702.51 km^3, SMB = 228.7332 Gt/yr")

ds.close()
