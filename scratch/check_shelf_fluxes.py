import netCDF4 as nc
import numpy as np

path = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
ds = nc.Dataset(path)

alpha_f = ds.variables["alpha_floating"][:]
alpha_g = ds.variables["alpha_grounded"][:]
alpha_r = ds.variables["alpha_rock"][:]
H = ds.variables["thickness"][:]
vx_0761 = ds.variables["vx_0761"][:]
vy_0761 = ds.variables["vy_0761"][:]
spd_0761 = ds.variables["speed_0761"][:]
cell_area = ds.variables["cell_area_wgs84_m2"][:]
ds.close()

dx, dy = 1000.0, 1000.0
spy = 31556926.0
RHO_ICE = 917.0
k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

shelf_active = (alpha_f > 0) & (H > 10.0)
ocean = (~shelf_active) & (alpha_g == 0) & (alpha_r == 0)

fe_so = shelf_active[:, :-1] & ocean[:, 1:]
fw_so = ocean[:, :-1] & shelf_active[:, 1:]
fn_so = ocean[:-1, :] & shelf_active[1:, :]
fs_so = shelf_active[:-1, :] & ocean[1:, :]

n_calv_shelf_faces = np.sum(fe_so) + np.sum(fw_so) + np.sum(fn_so) + np.sum(fs_so)

fe_u = np.maximum(0.0, vx_0761[:, :-1][fe_so])
fe_flx = RHO_ICE * H[:, :-1][fe_so] * fe_u * ds_x[:, :-1][fe_so] * 1e-12
fe_valid = ~np.isnan(fe_u)

fw_u = np.maximum(0.0, -vx_0761[:, 1:][fw_so])
fw_flx = RHO_ICE * H[:, 1:][fw_so] * fw_u * ds_x[:, 1:][fw_so] * 1e-12
fw_valid = ~np.isnan(fw_u)

fn_v = np.maximum(0.0, vy_0761[1:, :][fn_so])
fn_flx = RHO_ICE * H[1:, :][fn_so] * fn_v * ds_y[1:, :][fn_so] * 1e-12
fn_valid = ~np.isnan(fn_v)

fs_v = np.maximum(0.0, -vy_0761[:-1, :][fs_so])
fs_flx = RHO_ICE * H[:-1, :][fs_so] * fs_v * ds_y[:-1, :][fs_so] * 1e-12
fs_valid = ~np.isnan(fs_v)

obs_calv_flx = np.nansum(fe_flx) + np.nansum(fw_flx) + np.nansum(fn_flx) + np.nansum(fs_flx)
valid_faces = np.sum(fe_valid) + np.sum(fw_valid) + np.sum(fn_valid) + np.sum(fs_valid)
print(f"Floating shelf calving flux from NSIDC-0761 (450m multi-year): {obs_calv_flx:.2f} Gt/yr on {valid_faces}/{n_calv_shelf_faces} faces ({valid_faces/n_calv_shelf_faces*100:.1f}%)")
