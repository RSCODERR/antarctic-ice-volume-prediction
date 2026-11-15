import os
import time
import numpy as np
import pandas as pd
import netCDF4 as nc
import scipy.ndimage
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rmask

WORKSPACE_DIR = os.path.abspath("antarctic-ice-volume-prediction")
DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "processed")
NC_UNIFIED = os.path.join(DATA_DIR, "stage4_5_3", "stage4_5_3_unified_physical_fields.nc")
NC_QUALITY = os.path.join(DATA_DIR, "stage4_5_3", "stage4_5_3_quality_masks.nc")
NC_CAL = os.path.join(DATA_DIR, "stage4_7", "stage4_7_calibrated_velocity.nc")
IMBIE_SHP = os.path.join(WORKSPACE_DIR, "data", "raw", "imbie_basins", "IMBIE_AIS_Regional_Delineations", "IMBIE_AIS_Regional_Delineations.shp")
BM3_MASK = os.path.join(WORKSPACE_DIR, "data", "processed", "bedmap3_masks_peninsula_500m.tif")
BM3_THICK = os.path.join(WORKSPACE_DIR, "data", "processed", "bedmap3_thickness_peninsula_500m.tif")

print("Loading datasets...")
ds_u = nc.Dataset(NC_UNIFIED)
H = ds_u.variables["thickness"][:].astype(np.float64)
surface = ds_u.variables["surface"][:].astype(np.float64)
driving_stress = ds_u.variables["driving_stress"][:].astype(np.float64)
speed_0720 = ds_u.variables["speed_0720"][:].astype(np.float64)
error_0720 = ds_u.variables["error_0720"][:].astype(np.float64)
speed_0761 = ds_u.variables["speed_0761"][:].astype(np.float64)
error_0761 = ds_u.variables["error_0761"][:].astype(np.float64)
alpha_g = ds_u.variables["alpha_grounded"][:].astype(np.float64)
alpha_f = ds_u.variables["alpha_floating"][:].astype(np.float64)
alpha_r = ds_u.variables["alpha_rock"][:].astype(np.float64)
cell_area_wgs84 = ds_u.variables["cell_area_wgs84_m2"][:].astype(np.float64)
ds_u.close()

ds_q = nc.Dataset(NC_QUALITY)
qmask_0720 = ds_q.variables["quality_mask_nsidc0720"][:]
qmask_0761 = ds_q.variables["quality_mask_nsidc0761"][:]
ds_q.close()

ds_c = nc.Dataset(NC_CAL)
u_cal = ds_c.variables["u_calibrated"][:].astype(np.float64) / 31556926.0
v_cal = ds_c.variables["v_calibrated"][:].astype(np.float64) / 31556926.0
spd_cal = ds_c.variables["speed_calibrated"][:].astype(np.float64)
ds_c.close()

Ny, Nx = H.shape
dx, dy = 1000.0, 1000.0
spy = 31556926.0
RHO_ICE = 917.0
GRAVITY = 9.81
GLEN_B = 3.5e-25 ** (-1.0 / 3.0)
CB_FROZEN_RYDER = 8.168e6
C_OPT_IPP = 1.200e7
C_OPT_J = 1.550e7

grounded_active = (alpha_g > 0) & (H > 10.0)
n_active = int(np.sum(grounded_active))

# Load IMBIE basin masks
with rasterio.open(BM3_MASK) as src_m:
    bm3_mask_500 = src_m.read(1)
with rasterio.open(BM3_THICK) as src_t:
    bm3_thick_500 = src_t.read(1)
bm3_gr = (bm3_mask_500 == 1) & (bm3_thick_500 > 0) & (bm3_thick_500 != -9999)

gdf_imbie = gpd.read_file(IMBIE_SHP)
pen_basins = gdf_imbie[(gdf_imbie["Region"] == "Peninsula") & (gdf_imbie["Type"] == "Ice_sheet")].sort_values("Basin")

basin_masks_1km = {}
for _, row in pen_basins.iterrows():
    b_name = row["Basin"]
    with rasterio.open(BM3_MASK) as src:
        m_masked, _ = rmask(src, [row["geometry"]], crop=False, all_touched=False, nodata=-9999)
        m500 = (m_masked[0] == 1) & bm3_gr
        basin_masks_1km[b_name] = (m500.reshape(1700, 2, 1300, 2).mean(axis=(1, 3)) > 0) & (alpha_g > 0)

b_hp_act = basin_masks_1km["Hp-I"][grounded_active]
b_ipp_act = basin_masks_1km["I-Ipp"][grounded_active]
b_j_act = basin_masks_1km["Ipp-J"][grounded_active]

surface_smooth = scipy.ndimage.gaussian_filter(surface, sigma=1.0)
ds_dy_smooth, ds_dx_smooth = np.gradient(surface_smooth, -dy, dx)
slope_mag = np.sqrt(ds_dx_smooth**2 + ds_dy_smooth**2)

k_scale = np.sqrt((dx * dy) / cell_area_wgs84)
ds_x = dy / k_scale
ds_y = dx / k_scale

print("Evaluating robustness scenarios...")

# Baseline metrics on calibrated velocity
spd_cal_act = spd_cal[grounded_active]
obs_0720_act = speed_0720[grounded_active]
obs_0761_act = speed_0761[grounded_active]

# Face contour marine discharge helper
def calc_marine_flux(u_g, v_g):
    fe = grounded_active[:, :-1] & (~grounded_active[:, 1:])
    ue_out = np.maximum(0.0, u_g[:, :-1][fe])
    fe_flux = RHO_ICE * H[:, :-1][fe] * ue_out * ds_x[:, :-1][fe] * spy * 1e-12
    fe_mar = (alpha_f[:, 1:][fe] > 0) | ((alpha_f[:, 1:][fe] == 0) & (alpha_r[:, 1:][fe] == 0))

    fw = (~grounded_active[:, :-1]) & grounded_active[:, 1:]
    uw_out = np.maximum(0.0, -u_g[:, 1:][fw])
    fw_flux = RHO_ICE * H[:, 1:][fw] * uw_out * ds_x[:, 1:][fw] * spy * 1e-12
    fw_mar = (alpha_f[:, :-1][fw] > 0) | ((alpha_f[:, :-1][fw] == 0) & (alpha_r[:, :-1][fw] == 0))

    fn = (~grounded_active[:-1, :]) & grounded_active[1:, :]
    un_out = np.maximum(0.0, v_g[1:, :][fn])
    fn_flux = RHO_ICE * H[1:, :][fn] * un_out * ds_y[1:, :][fn] * spy * 1e-12
    fn_mar = (alpha_f[:-1, :][fn] > 0) | ((alpha_f[:-1, :][fn] == 0) & (alpha_r[:-1, :][fn] == 0))

    fs = grounded_active[:-1, :] & (~grounded_active[1:, :])
    us_out = np.maximum(0.0, -v_g[:-1, :][fs])
    fs_flux = RHO_ICE * H[:-1, :][fs] * us_out * ds_y[:-1, :][fs] * spy * 1e-12
    fs_mar = (alpha_f[1:, :][fs] > 0) | ((alpha_f[1:, :][fs] == 0) & (alpha_r[1:, :][fs] == 0))

    return float(np.sum(fe_flux[fe_mar]) + np.sum(fw_flux[fw_mar]) + np.sum(fn_flux[fn_mar]) + np.sum(fs_flux[fs_mar]))

base_mar_flux = calc_marine_flux(u_cal, v_cal)
print(f"Base Calibrated Marine Flux: {base_mar_flux:.2f} Gt/yr")

# Robustness grid
# 1. Standard baseline gate
std_gate = (driving_stress[grounded_active] > 500e3) & (slope_mag[grounded_active] > 0.10)

# Scenarios to test:
scenarios = [
    {
        "Scenario_ID": "ROB-01",
        "Category": "Observation Quality Mask",
        "Description": "Baseline: NSIDC-0720 Quality Mask = 1 (Direct observations only)",
        "Obs_Data": obs_0720_act,
        "Valid_Mask": (~np.isnan(obs_0720_act)) & (qmask_0720[grounded_active] == 1) & (~std_gate),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-02",
        "Category": "Observation Dataset Selection",
        "Description": "Alternative: NSIDC-0761 (450m Multi-Year Reference, Direct-only: qm=1)",
        "Obs_Data": obs_0761_act,
        "Valid_Mask": (~np.isnan(obs_0761_act)) & (qmask_0761[grounded_active] == 1) & (~std_gate),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-03",
        "Category": "Observation Dataset Selection",
        "Description": "Alternative: NSIDC-0761 (Direct + Interpolated/Aggregated: qm in [1, 2])",
        "Obs_Data": obs_0761_act,
        "Valid_Mask": (~np.isnan(obs_0761_act)) & (np.isin(qmask_0761[grounded_active], [1, 2])) & (~std_gate),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-04",
        "Category": "Spatial Cross-Validation",
        "Description": "50% Spatial Subsampling: Even Cells ((i+j)%2 == 0)",
        "Obs_Data": obs_0720_act,
        "Valid_Mask": (~np.isnan(obs_0720_act)) & (qmask_0720[grounded_active] == 1) & (~std_gate) & (((np.indices((Ny, Nx))[0] + np.indices((Ny, Nx))[1])[grounded_active]) % 2 == 0),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-05",
        "Category": "Spatial Cross-Validation",
        "Description": "50% Spatial Subsampling: Odd Cells ((i+j)%2 == 1)",
        "Obs_Data": obs_0720_act,
        "Valid_Mask": (~np.isnan(obs_0720_act)) & (qmask_0720[grounded_active] == 1) & (~std_gate) & (((np.indices((Ny, Nx))[0] + np.indices((Ny, Nx))[1])[grounded_active]) % 2 == 1),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-06",
        "Category": "Extreme-Slope Quality Gate",
        "Description": "Strict Quality Gate: |grad s| > 0.08 & tau_d > 400 kPa (Gating 712 cells)",
        "Obs_Data": obs_0720_act,
        "Valid_Mask": (~np.isnan(obs_0720_act)) & (qmask_0720[grounded_active] == 1) & (~((driving_stress[grounded_active] > 400e3) & (slope_mag[grounded_active] > 0.08))),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-07",
        "Category": "Extreme-Slope Quality Gate",
        "Description": "Permissive Quality Gate: |grad s| > 0.15 & tau_d > 600 kPa (Gating 182 cells)",
        "Obs_Data": obs_0720_act,
        "Valid_Mask": (~np.isnan(obs_0720_act)) & (qmask_0720[grounded_active] == 1) & (~((driving_stress[grounded_active] > 600e3) & (slope_mag[grounded_active] > 0.15))),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    },
    {
        "Scenario_ID": "ROB-08",
        "Category": "Extreme-Slope Quality Gate",
        "Description": "Ungated Cost Function: Zero cells excluded from loss",
        "Obs_Data": obs_0720_act,
        "Valid_Mask": (~np.isnan(obs_0720_act)) & (qmask_0720[grounded_active] == 1),
        "C_ipp_Pa_m_s": 1.200e7,
        "C_j_Pa_m_s": 1.550e7
    }
]

for sc in scenarios:
    m = spd_cal_act[sc["Valid_Mask"]]
    o = sc["Obs_Data"][sc["Valid_Mask"]]
    log_rmsd = float(np.sqrt(np.mean((np.log10(np.maximum(m, 0.1)) - np.log10(np.maximum(o, 0.1)))**2)))
    mean_bias = float(np.mean(m - o))
    mae = float(np.mean(np.abs(m - o)))
    rmse = float(np.sqrt(np.mean((m - o)**2)))
    print(f"[{sc['Scenario_ID']}] {sc['Description']}: N={len(m):,}, Bias={mean_bias:+6.2f} m/yr, LogRMSD={log_rmsd:.4f}, RMSE={rmse:.2f} m/yr")

