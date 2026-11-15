import geopandas as gpd

shp_path = 'antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp'
gdf = gpd.read_file(shp_path)
gdf['area_km2'] = gdf.geometry.area / 1e6
for idx, row in gdf[gdf['Region'] == 'Peninsula'].iterrows():
    b = row.geometry.bounds
    print(f"{row['Basin']:6s} {row['Type']:10s}: Area={row['area_km2']:8.1f} km2, bounds=({b[0]:.0f}, {b[1]:.0f}, {b[2]:.0f}, {b[3]:.0f})")

