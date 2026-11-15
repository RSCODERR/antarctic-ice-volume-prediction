import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.ops import unary_union

shp_path = 'antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp'
gdf = gpd.read_file(shp_path)

# 1. Project basins (Phase 2.6 defined as Ice_sheet mainland only)
b_hpi_proj = gdf[(gdf['Basin'] == 'Hp-I') & (gdf['Type'] == 'Ice_sheet')].geometry.iloc[0]
b_iipp_proj = gdf[(gdf['Basin'] == 'I-Ipp') & (gdf['Type'] == 'Ice_sheet')].geometry.iloc[0]
b_ippj_proj = gdf[(gdf['Basin'] == 'Ipp-J') & (gdf['Type'] == 'Ice_sheet')].geometry.iloc[0]
b_doma_proj = unary_union([b_hpi_proj, b_iipp_proj, b_ippj_proj])

proj_basins = {
    'Hp-I': b_hpi_proj,
    'I-Ipp': b_iipp_proj,
    'Ipp-J': b_ippj_proj,
    'Domain_A': b_doma_proj
}

# 2. Full IMBIE Drainage Sectors (Ice_sheet + Islands, which defines ISMIP6 sectors)
s_hpi_full = unary_union(gdf[gdf['Basin'] == 'Hp-I'].geometry)
s_iipp_full = unary_union(gdf[gdf['Basin'] == 'I-Ipp'].geometry)
s_ippj_full = unary_union(gdf[gdf['Basin'] == 'Ipp-J'].geometry)
s_r3_full = unary_union([s_hpi_full, s_iipp_full, s_ippj_full])

full_sectors = {
    'Sector_Hp_I': s_hpi_full,
    'Sector_I_Ipp': s_iipp_full,
    'Sector_Ipp_J': s_ippj_full,
    'Region_3': s_r3_full
}

# Cross-intersection matrix
rows = []
for p_name, p_geom in proj_basins.items():
    p_area = p_geom.area / 1e6
    for s_name, s_geom in full_sectors.items():
        inter = p_geom.intersection(s_geom)
        inter_area = inter.area / 1e6
        pct_proj = (inter_area / p_area) * 100.0 if p_area > 0 else 0.0
        s_area = s_geom.area / 1e6
        pct_sect = (inter_area / s_area) * 100.0 if s_area > 0 else 0.0
        
        rows.append({
            'Project_Basin': p_name,
            'Project_Basin_Area_km2': p_area,
            'ISMIP6_Sector_or_Region': s_name,
            'ISMIP6_Sector_Area_km2': s_area,
            'Intersection_Area_km2': inter_area,
            'Pct_Project_Basin_Covered': pct_proj,
            'Pct_Sector_Covered_by_Basin': pct_sect
        })

df_inter = pd.DataFrame(rows)
print(df_inter.to_string())

# Check unassigned / multiply assigned areas
print("\n=== MULTIPLY ASSIGNED / OVERLAP CHECKS ===")
print("Project basins overlap with each other:")
print("  Hp-I & I-Ipp:", b_hpi_proj.intersection(b_iipp_proj).area / 1e6)
print("  I-Ipp & Ipp-J:", b_iipp_proj.intersection(b_ippj_proj).area / 1e6)
print("  Hp-I & Ipp-J:", b_hpi_proj.intersection(b_ippj_proj).area / 1e6)

print("\nISMIP6 Sectors overlap with each other:")
print("  Hp-I & I-Ipp:", s_hpi_full.intersection(s_iipp_full).area / 1e6)
print("  I-Ipp & Ipp-J:", s_iipp_full.intersection(s_ippj_full).area / 1e6)
print("  Hp-I & Ipp-J:", s_hpi_full.intersection(s_ippj_full).area / 1e6)

print("\nUnassigned Area in Region 3 not covered by project mainland Domain A:")
unassigned_r3 = s_r3_full.difference(b_doma_proj).area / 1e6
print(f"  Unassigned peripheral/island area in Region 3: {unassigned_r3:.1f} km2 ({(unassigned_r3 / (s_r3_full.area/1e6))*100:.2f}%)")
