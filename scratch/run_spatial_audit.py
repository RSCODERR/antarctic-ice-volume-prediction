import os
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from matplotlib.patches import Patch

# Paths
BASE_DIR = os.path.abspath('antarctic-ice-volume-prediction')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
TABLES_DIR = os.path.join(REPORTS_DIR, 'tables')
FIGURES_DIR = os.path.join(REPORTS_DIR, 'figures')
ARTIFACT_DIR = r"C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f"
ARTIFACT_FIG_DIR = os.path.join(ARTIFACT_DIR, 'figures')

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(ARTIFACT_FIG_DIR, exist_ok=True)

shp_path = os.path.join(BASE_DIR, 'data', 'raw', 'imbie_basins', 'IMBIE_AIS_Regional_Delineations', 'IMBIE_AIS_Regional_Delineations.shp')
gdf = gpd.read_file(shp_path)

# Project Basins (Phase 2.6 defined as Ice_sheet mainland only)
b_hpi = gdf[(gdf['Basin'] == 'Hp-I') & (gdf['Type'] == 'Ice_sheet')].geometry.iloc[0]
b_iipp = gdf[(gdf['Basin'] == 'I-Ipp') & (gdf['Type'] == 'Ice_sheet')].geometry.iloc[0]
b_ippj = gdf[(gdf['Basin'] == 'Ipp-J') & (gdf['Type'] == 'Ice_sheet')].geometry.iloc[0]
b_doma = unary_union([b_hpi, b_iipp, b_ippj])

proj_dict = {
    'Hp-I': b_hpi,
    'I-Ipp': b_iipp,
    'Ipp-J': b_ippj,
    'Domain_A': b_doma
}

# Full IMBIE Drainage Sectors (Ice_sheet + Islands)
s_hpi = unary_union(gdf[gdf['Basin'] == 'Hp-I'].geometry)
s_iipp = unary_union(gdf[gdf['Basin'] == 'I-Ipp'].geometry)
s_ippj = unary_union(gdf[gdf['Basin'] == 'Ipp-J'].geometry)
s_r3 = unary_union([s_hpi, s_iipp, s_ippj])

sector_dict = {
    'Sector_Hp_I (claimed Sector 16)': s_hpi,
    'Sector_I_Ipp (claimed Sector 17)': s_iipp,
    'Sector_Ipp_J (claimed Sector 18)': s_ippj,
    'Region_3 (claimed Domain A)': s_r3
}

# Table calculation
overlap_rows = []

# Pairings to audit
pairings = [
    ('Hp-I', 'Sector_Hp_I (claimed Sector 16)', s_hpi),
    ('Hp-I', 'Sector_I_Ipp (claimed Sector 17)', s_iipp),
    ('Hp-I', 'Sector_Ipp_J (claimed Sector 18)', s_ippj),
    ('I-Ipp', 'Sector_Hp_I (claimed Sector 16)', s_hpi),
    ('I-Ipp', 'Sector_I_Ipp (claimed Sector 17)', s_iipp),
    ('I-Ipp', 'Sector_Ipp_J (claimed Sector 18)', s_ippj),
    ('Ipp-J', 'Sector_Hp_I (claimed Sector 16)', s_hpi),
    ('Ipp-J', 'Sector_I_Ipp (claimed Sector 17)', s_iipp),
    ('Ipp-J', 'Sector_Ipp_J (claimed Sector 18)', s_ippj),
    ('Domain_A', 'Region_3 (claimed Domain A)', s_r3)
]

for p_name, s_label, s_geom in pairings:
    p_geom = proj_dict[p_name]
    p_area = p_geom.area / 1e6
    s_area = s_geom.area / 1e6
    inter = p_geom.intersection(s_geom)
    inter_area = inter.area / 1e6
    pct_p = (inter_area / p_area) * 100.0 if p_area > 0 else 0.0
    pct_s = (inter_area / s_area) * 100.0 if s_area > 0 else 0.0
    
    # Geographic assessment
    if pct_p > 99.9 and pct_s > 99.9:
        status = "Exact Spatial Equivalence"
    elif pct_p > 99.9 and pct_s < 99.9:
        status = f"Strict Subset (Basin is {pct_s:.1f}% of Sector; Sector has {s_area - inter_area:.1f} km2 peripheral islands)"
    elif inter_area == 0:
        status = "Zero Spatial Overlap (Disjoint)"
    else:
        status = "Partial Overlap"
        
    overlap_rows.append({
        'Project_Basin': p_name,
        'Project_Basin_Area_km2': round(p_area, 2),
        'ISMIP6_Sector_or_Region': s_label,
        'ISMIP6_Sector_Area_km2': round(s_area, 2),
        'Intersection_Area_km2': round(inter_area, 2),
        'Pct_Project_Basin_Covered': round(pct_p, 2),
        'Pct_Sector_Covered_by_Basin': round(pct_s, 2),
        'Unassigned_Sector_Area_km2': round(s_area - inter_area if pct_p > 0 else 0.0, 2),
        'Spatial_Relationship_Status': status,
        'Proxy_Classification': 'ISMIP6 Regional Sector Proxy (NOT Exact Basin)' if pct_s < 99.9 else 'Exact Basin'
    })

df_overlap = pd.DataFrame(overlap_rows)
out_csv = os.path.join(TABLES_DIR, 'ismip6_sector_project_basin_overlap.csv')
df_overlap.to_csv(out_csv, index=False)
print(f"Saved {out_csv} ({len(df_overlap)} rows)")

# Generate Spatial Overlay Map
fig, axes = plt.subplots(1, 4, figsize=(24, 8), dpi=200)

# Colors
c_hpi = '#1f77b4'
c_iipp = '#2ca02c'
c_ippj = '#d62728'
c_isl = '#ff7f0e'

# Panel 1: Project Basins (Mainland Ice Sheet only)
ax1 = axes[0]
gdf[(gdf['Basin'] == 'Hp-I') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax1, color=c_hpi, edgecolor='black', linewidth=0.5, label='Hp-I (Mainland)')
gdf[(gdf['Basin'] == 'I-Ipp') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax1, color=c_iipp, edgecolor='black', linewidth=0.5, label='I-Ipp (Mainland)')
gdf[(gdf['Basin'] == 'Ipp-J') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax1, color=c_ippj, edgecolor='black', linewidth=0.5, label='Ipp-J (Mainland)')
ax1.set_title("1. Phase 2.6 Project Basins\n(Mainland Ice Sheet Only: 232,678 km²)", fontsize=11, fontweight='bold')
ax1.set_xlabel("Polar Stereographic X (m)")
ax1.set_ylabel("Polar Stereographic Y (m)")
ax1.grid(True, linestyle='--', alpha=0.5)
legend_elements1 = [
    Patch(facecolor=c_hpi, edgecolor='black', label='Hp-I (110,265 km²)'),
    Patch(facecolor=c_iipp, edgecolor='black', label='I-Ipp (61,053 km²)'),
    Patch(facecolor=c_ippj, edgecolor='black', label='Ipp-J (61,360 km²)')
]
ax1.legend(handles=legend_elements1, loc='lower left', fontsize=9)

# Panel 2: Full IMBIE / ISMIP6 Sectors (Mainland + Islands)
ax2 = axes[1]
gdf[gdf['Region'] == 'Peninsula'].plot(ax=ax2, color='#e0e0e0', edgecolor='gray', linewidth=0.5)
gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Islands')].plot(ax=ax2, color=c_isl, edgecolor='darkorange', linewidth=0.5)
gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax2, color='none', edgecolor='black', linewidth=0.8)
ax2.set_title("2. ISMIP6 / IMBIE Full Sectors\n(Mainland + Peripheral Islands: 314,912 km²)", fontsize=11, fontweight='bold')
ax2.set_xlabel("Polar Stereographic X (m)")
ax2.set_ylabel("Polar Stereographic Y (m)")
ax2.grid(True, linestyle='--', alpha=0.5)
legend_elements2 = [
    Patch(facecolor='none', edgecolor='black', label='Mainland Core (73.9%)'),
    Patch(facecolor=c_isl, edgecolor='darkorange', label='Peripheral Islands (82,234 km², 26.1%)')
]
ax2.legend(handles=legend_elements2, loc='lower left', fontsize=9)

# Panel 3: Spatial Overlay showing mismatch / unassigned area
ax3 = axes[2]
# Plot full sectors as background
gdf[gdf['Region'] == 'Peninsula'].plot(ax=ax3, color='#fff2e6', edgecolor='darkorange', linewidth=0.8)
# Plot project mainland on top
gdf[(gdf['Basin'] == 'Hp-I') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax3, color=c_hpi, alpha=0.7, edgecolor='black', linewidth=0.5)
gdf[(gdf['Basin'] == 'I-Ipp') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax3, color=c_iipp, alpha=0.7, edgecolor='black', linewidth=0.5)
gdf[(gdf['Basin'] == 'Ipp-J') & (gdf['Type'] == 'Ice_sheet')].plot(ax=ax3, color=c_ippj, alpha=0.7, edgecolor='black', linewidth=0.5)
# Highlight Alexander Island and western archipelago
gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Islands')].plot(ax=ax3, color='orange', alpha=0.8, edgecolor='red', linewidth=0.5)
ax3.set_title("3. Spatial Discrepancy Overlay\n(Orange = Excluded Islands in ISMIP6 Sectors)", fontsize=11, fontweight='bold')
ax3.set_xlabel("Polar Stereographic X (m)")
ax3.set_ylabel("Polar Stereographic Y (m)")
ax3.grid(True, linestyle='--', alpha=0.5)
legend_elements3 = [
    Patch(facecolor=c_hpi, alpha=0.7, label='Project Hp-I Core'),
    Patch(facecolor=c_iipp, alpha=0.7, label='Project I-Ipp Core'),
    Patch(facecolor=c_ippj, alpha=0.7, label='Project Ipp-J Core'),
    Patch(facecolor='orange', edgecolor='red', label='Unassigned Islands (Alexander, Adelaide, etc.)')
]
ax3.legend(handles=legend_elements3, loc='lower left', fontsize=9)

# Panel 4: Area Comparison Bar Chart
ax4 = axes[3]
basins = ['Hp-I', 'I-Ipp', 'Ipp-J', 'Domain A']
proj_vals = [b_hpi.area/1e6, b_iipp.area/1e6, b_ippj.area/1e6, b_doma.area/1e6]
sect_vals = [s_hpi.area/1e6, s_iipp.area/1e6, s_ippj.area/1e6, s_r3.area/1e6]
x = np.arange(len(basins))
w = 0.35

rects1 = ax4.bar(x - w/2, proj_vals, w, label='Project Basin (Mainland)', color='#3b528b')
rects2 = ax4.bar(x + w/2, sect_vals, w, label='ISMIP6 Full Sector', color='#5ec962')

ax4.set_title("4. Area Discrepancy Breakdown\n(Mainland Basin vs ISMIP6 Sector)", fontsize=11, fontweight='bold')
ax4.set_ylabel("Area (km²)", fontsize=10)
ax4.set_xticks(x)
ax4.set_xticklabels(basins, fontsize=10)
ax4.grid(True, linestyle='--', alpha=0.5, axis='y')
ax4.legend(loc='upper left', fontsize=9)

for rect in rects1:
    h = rect.get_height()
    ax4.annotate(f"{h:,.0f}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=8)
for rect in rects2:
    h = rect.get_height()
    ax4.annotate(f"{h:,.0f}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=8)

plt.suptitle("PHASE 5.1.1: SPATIAL SECTOR-TO-BASIN FORENSIC AUDIT & OVERLAY DISCREPANCY", fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])

out_fig = os.path.join(FIGURES_DIR, 'fig13_ismip6_sector_basin_overlay.png')
plt.savefig(out_fig, dpi=200)
plt.close()
print(f"Saved figure to {out_fig}")

# Copy to artifacts directory
shutil.copy2(out_fig, os.path.join(ARTIFACT_FIG_DIR, 'fig13_ismip6_sector_basin_overlay.png'))
print("Copied figure to artifacts directory.")

