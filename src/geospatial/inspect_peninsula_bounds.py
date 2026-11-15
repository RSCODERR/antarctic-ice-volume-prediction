import geopandas as gpd

shp_path = "antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"
gdf = gpd.read_file(shp_path)

peninsula_gdf = gdf[gdf['Region'] == 'Peninsula']
print("Peninsula basins in IMBIE:")
for idx, row in peninsula_gdf.iterrows():
    bounds = row.geometry.bounds
    area_km2 = row.geometry.area / 1e6
    print(f"Basin: {row['Basin']:6s} | Type: {row['Type']:10s} | Area: {area_km2:10.1f} km² | Bounds: (minx={bounds[0]:.0f}, miny={bounds[1]:.0f}, maxx={bounds[2]:.0f}, maxy={bounds[3]:.0f})")

print("\nCombined Peninsula extent (Ice_sheet + Islands):")
total_bounds = peninsula_gdf.total_bounds
print(f"MinX: {total_bounds[0]:.0f}, MinY: {total_bounds[1]:.0f}, MaxX: {total_bounds[2]:.0f}, MaxY: {total_bounds[3]:.0f}")

ice_sheet_only = peninsula_gdf[peninsula_gdf['Type'] == 'Ice_sheet']
islands_only = peninsula_gdf[peninsula_gdf['Type'] == 'Islands']
print(f"Total Ice_sheet Area: {ice_sheet_only.geometry.area.sum() / 1e6:.1f} km²")
print(f"Total Islands Area:   {islands_only.geometry.area.sum() / 1e6:.1f} km²")
print(f"Combined Total Area:  {peninsula_gdf.geometry.area.sum() / 1e6:.1f} km²")

