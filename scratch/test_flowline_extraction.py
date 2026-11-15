import numpy as np
import netCDF4 as nc

def lonlat_to_epsg3031(lon, lat):
    try:
        from pyproj import Transformer
        trans = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
        return trans.transform(lon, lat)
    except Exception:
        a = 6378137.0
        e_sq = 0.00669437999014
        e = np.sqrt(e_sq)
        phi = np.radians(lat)
        lam = np.radians(lon)
        phi_c = np.radians(-71.0)
        m_c = np.cos(-phi_c) / np.sqrt(1.0 - e_sq * np.sin(-phi_c)**2)
        t_c = np.tan(np.pi/4.0 - (-phi_c)/2.0) / ((1.0 - e*np.sin(-phi_c))/(1.0 + e*np.sin(-phi_c)))**(e/2.0)
        t = np.tan(np.pi/4.0 - (-phi)/2.0) / ((1.0 - e*np.sin(-phi))/(1.0 + e*np.sin(-phi)))**(e/2.0)
        rho = a * m_c * t / t_c
        x = rho * np.sin(lam)
        y = -rho * np.cos(lam)
        return x, y

# Define flowline endpoints (divide -> terminus)
flowline_defs = {
    "FL_HPI_01 (Ryder/Bertram)": {
        "divide": (-65.0, -71.5),
        "terminus": (-68.5, -71.2),
        "typical_width": 15000.0,
    },
    "FL_IIPP_01 (Flanders Bay)": {
        "divide": (-62.0, -65.0),
        "terminus": (-63.0, -64.8),
        "typical_width": 4000.0,
    },
    "FL_IPPJ_02 (Crane Glacier)": {
        "divide": (-64.5, -65.3),
        "terminus": (-63.1, -65.4),
        "typical_width": 6000.0,
    }
}

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

dx_grid = xs[1] - xs[0]
dy_grid = ys[1] - ys[0] # negative

print("Grid x:", xs[0], xs[-1], "y:", ys[0], ys[-1], "dx:", dx_grid, "dy:", dy_grid)

for fl_name, info in flowline_defs.items():
    p_div = lonlat_to_epsg3031(*info["divide"])
    p_term = lonlat_to_epsg3031(*info["terminus"])
    dist = np.hypot(p_term[0] - p_div[0], p_term[1] - p_div[1])
    n_pts = int(round(dist / 500.0))
    print(f"\n--- {fl_name} ---")
    print(f"Divide EPSG:3031: {p_div}, Terminus EPSG:3031: {p_term}, Total length: {dist/1e3:.1f} km, {n_pts} cells @ 500m")
    
    t = np.linspace(0, 1, n_pts)
    line_x = p_div[0] + t * (p_term[0] - p_div[0])
    line_y = p_div[1] + t * (p_term[1] - p_div[1])
    
    cols = np.clip(np.round((line_x - xs[0]) / dx_grid).astype(int), 0, len(xs)-1)
    rows = np.clip(np.round((line_y - ys[0]) / dy_grid).astype(int), 0, len(ys)-1)
    
    masks = ds.variables['mask'][rows, cols]
    thick = ds.variables['thickness'][rows, cols]
    surf = ds.variables['surface'][rows, cols]
    bed = ds.variables['bed'][rows, cols]
    firn = ds.variables['firn'][rows, cols]
    
    print(f"Mask values: {np.unique(masks, return_counts=True)}")
    print(f"Thickness: min={np.nanmin(thick):.1f}m, mean={np.nanmean(thick):.1f}m, max={np.nanmax(thick):.1f}m")
    print(f"Surface: min={np.nanmin(surf):.1f}m, max={np.nanmax(surf):.1f}m")
    print(f"Bed: min={np.nanmin(bed):.1f}m, max={np.nanmax(bed):.1f}m")
    print(f"Firn: min={np.nanmin(firn):.1f}m, mean={np.nanmean(firn):.1f}m, max={np.nanmax(firn):.1f}m")

ds.close()

