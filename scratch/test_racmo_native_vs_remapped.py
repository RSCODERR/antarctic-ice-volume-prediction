"""
Compare Native RACMO 5.5km vs Remapped 1km SMB conservation.
"""
import sys, os
sys.path.insert(0, ".")
import netCDF4 as nc
import numpy as np
import pyproj
import geopandas as gpd
from shapely.geometry import Point
from rasterio import features
import rasterio

# 1. Load native RACMO
ds_racmo = nc.Dataset("data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc")
lat = ds_racmo.variables['lat'][:] # (294, 390)
lon = ds_racmo.variables['lon'][:]
smb_monthly = ds_racmo.variables['smb'][:]
smb_annual = smb_monthly[:480, 0, :, :].reshape(40, 12, 294, 390).sum(axis=1).mean(axis=0) # mm w.e./yr

transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
rx, ry = transformer.transform(lon, lat)

# Snyder scale factor for native RACMO cell ellipsoidal area
# At standard parallel 71 S, cell spacing in rotated pole is 0.05 deg ~ 5.55 km
# Each native cell has area A_native
# Let's compute exact ellipsoidal cell area for each RACMO cell
from src.geospatial.audit_distortion import compute_scale_factor_grid

# 2. Polygon intersection for native RACMO
gdf_imbie = gpd.read_file("data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp")
pen_basins = gdf_imbie[(gdf_imbie["Region"] == "Peninsula") & (gdf_imbie["Type"] == "Ice_sheet")].sort_values("Basin")

print("Auditing native RACMO cells in Domain A basins...")
native_basin_mass = {}
native_basin_area = {}

# Compute cell area using pyproj Geod for exact ellipsoidal area of native cells
geod = pyproj.Geod(ellps="WGS84")

# Approximate grid spacing: dlat = 0.05, dlon = 0.05 in rotated pole
# In geographic coords, compute pixel area via geod:
# Native RACMO cell corners:
dlon = 0.05
dlat = 0.05

for _, row in pen_basins.iterrows():
    b_name = row["Basin"]
    geom = row["geometry"]
    # Point-in-polygon test for RACMO points
    # Quick filter: bounding box
    minx, miny, maxx, maxy = geom.bounds
    in_bbox = (rx >= minx) & (rx <= maxx) & (ry >= miny) & (ry <= maxy)
    idx_y, idx_x = np.where(in_bbox)
    
    in_poly = []
    for iy, ix in zip(idx_y, idx_x):
        pt = Point(rx[iy, ix], ry[iy, ix])
        if geom.contains(pt):
            in_poly.append((iy, ix))
            
    print(f"Basin {b_name}: {len(in_poly)} native RACMO cells inside basin")
    if in_poly:
        iy_arr, ix_arr = zip(*in_poly)
        smb_vals = smb_annual[iy_arr, ix_arr]
        # Native cell area in EPSG:3031
        # ~ 5.5 km x 5.5 km = ~30.8 km2 (distorted by polar stereo scale factor k^2)
        # Using Snyder scale factor k at each lat:
        lat_rad = np.radians(np.abs(lat[iy_arr, ix_arr]))
        # Polar stereographic scale factor at 71S: k = (1 + sin 71) / (1 + sin lat)
        k = (1.0 + np.sin(np.radians(71.0))) / (1.0 + np.sin(lat_rad))
        cell_area_native_km2 = (5.55 * 5.55) / (k**2)
        
        tot_area = np.sum(cell_area_native_km2)
        tot_mass = np.sum(smb_vals * cell_area_native_km2) * 1e-6
        mean_smb = np.sum(smb_vals * cell_area_native_km2) / tot_area
        native_basin_mass[b_name] = tot_mass
        native_basin_area[b_name] = tot_area
        print(f"  Native Basin {b_name}: Area ~ {tot_area:.1f} km2, Mean SMB = {mean_smb:.1f} mm/yr, Mass = {tot_mass:.2f} Gt/yr")

