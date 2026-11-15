import numpy as np
import netCDF4 as nc

def lonlat_to_epsg3031(lon, lat):
    # Standard Antarctic Polar Stereographic (EPSG:3031):
    # lat_ts = -71.0, lon_0 = 0.0, WGS84
    # Let's see if pyproj is available
    try:
        from pyproj import Transformer
        trans = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
        return trans.transform(lon, lat)
    except Exception as e:
        # Fallback ellipsoidal formula or spherical
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

gates = [
    ("GATE_HP_01 (Ryder)", -68.45, -71.25),
    ("GATE_IPP_01 (Leonardo/Flanders)", -62.1, -64.72),
    ("GATE_IPJ_01 (Crane)", -63.2, -65.35)
]

for name, lon, lat in gates:
    x, y = lonlat_to_epsg3031(lon, lat)
    print(f"{name}: lon={lon}, lat={lat} -> x={x:.1f}, y={y:.1f}")

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
print(f"Grid x: [{xs.min()}, {xs.max()}], y: [{ys.min()}, {ys.max()}]")

for name, lon, lat in gates:
    gx, gy = lonlat_to_epsg3031(lon, lat)
    col = int(round((gx - xs[0]) / (xs[1] - xs[0])))
    row = int(round((gy - ys[0]) / (ys[1] - ys[0])))
    print(f"{name} grid index: row={row}, col={col}")
    if 0 <= row < len(ys) and 0 <= col < len(xs):
        thick = ds.variables['thickness'][row, col]
        surf = ds.variables['surface'][row, col]
        bed = ds.variables['bed'][row, col]
        mask = ds.variables['mask'][row, col]
        firn = ds.variables['firn'][row, col]
        print(f"  BedMachine data: mask={mask}, H={thick:.1f}m, s={surf:.1f}m, bed={bed:.1f}m, firn={firn:.1f}m")
    else:
        print("  Out of bounds!")

ds.close()

