"""
Phase 2 Geospatial Visualizations: Antarctic Peninsula Domain and Baseline Data
Generates publication-quality cartographic figures for:
1. Study region boundary and IMBIE drainage basins (Hp-I, I-Ipp, Ipp-J).
2. Bedmap3 ice thickness grid (500 m).
3. Baseline ice classification and surface type masks.
4. Bedmap3 ice thickness uncertainty grid (500 m).
5. Statistical distribution and basin-wise thickness profiles.
"""

import os
os.environ['MPLCONFIGDIR'] = os.path.abspath('antarctic-ice-volume-prediction/data/processed/.matplotlib')
import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.ticker as ticker

# Setup plot styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

FIGURES_DIR = "antarctic-ice-volume-prediction/reports/figures"
PROCESSED_DIR = "antarctic-ice-volume-prediction/data/processed"
IMBIE_SHP = "antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"

os.makedirs(FIGURES_DIR, exist_ok=True)

# Load Peninsula basins
print("Loading IMBIE shapefile...")
gdf_all = gpd.read_file(IMBIE_SHP)
peninsula_gdf = gdf_all[gdf_all['Region'] == 'Peninsula'].copy()
peninsula_gdf['area_km2'] = peninsula_gdf.geometry.area / 1e6

# -------------------------------------------------------------
# FIGURE 1: Study Domain and Drainage Basins
# -------------------------------------------------------------
print("Generating Map 1: Antarctic Peninsula Drainage Basins...")
fig, ax = plt.subplots(figsize=(10, 12), dpi=300)

# Colors for basins
basin_colors = {
    'Hp-I': '#2b83ba',   # Palmer Land (West)
    'I-Ipp': '#abdda4',  # Graham Land (North)
    'Ipp-J': '#fdae61'   # Palmer Land (East)
}

# Plot Continental Ice Sheet polygons
for basin, color in basin_colors.items():
    subset = peninsula_gdf[(peninsula_gdf['Basin'] == basin) & (peninsula_gdf['Type'] == 'Ice_sheet')]
    subset.plot(ax=ax, color=color, edgecolor='#1b2a47', linewidth=1.2, alpha=0.85, label=f"Basin {basin} (Ice Sheet)")

# Plot Island polygons with hatching
for basin, color in basin_colors.items():
    subset = peninsula_gdf[(peninsula_gdf['Basin'] == basin) & (peninsula_gdf['Type'] == 'Islands')]
    subset.plot(ax=ax, color=color, edgecolor='#5c2a1e', linewidth=0.8, hatch='///', alpha=0.7, label=f"Basin {basin} (Islands)")

# Set bounds to Peninsula extent with margin
ax.set_xlim(-2700000, -1400000)
ax.set_ylim(250000, 1950000)

# Format coordinates in km (EPSG:3031)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x/1000):,} km"))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f"{int(y/1000):,} km"))
ax.set_xlabel("Polar Stereographic X (m / km from Pole)", fontweight='bold')
ax.set_ylabel("Polar Stereographic Y (m / km from Pole)", fontweight='bold')

# Gridlines
ax.grid(True, linestyle='--', alpha=0.5, color='gray')

# Add geographic feature callouts
ax.text(-2250000, 1550000, "Graham Land\n(Basin I-Ipp)", fontsize=11, fontweight='bold', color='#1a3826', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))
ax.text(-1950000, 800000, "Palmer Land\n(Basin Hp-I / Ipp-J)", fontsize=11, fontweight='bold', color='#08306b', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))
ax.text(-2550000, 750000, "Alexander Island\n(Islands Hp-I)", fontsize=9, fontstyle='italic', color='#4a148c', ha='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))
ax.text(-1750000, 1400000, "Larsen C\nIce Shelf", fontsize=9, fontstyle='italic', color='#004d40', ha='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))

# Title and subtitle
plt.title("Antarctic Peninsula Study Domain & IMBIE Drainage Basins\nOfficial MEaSUREs / IMBIE Delineations (EPSG:3031)",
          fontsize=13, fontweight='bold', pad=15)

# Custom legend
legend_elements = [
    mpatches.Patch(facecolor='#abdda4', edgecolor='#1b2a47', label='I-Ipp: Graham Land (61,053 km² ice sheet)'),
    mpatches.Patch(facecolor='#2b83ba', edgecolor='#1b2a47', label='Hp-I: W. Palmer Land (110,266 km² ice sheet)'),
    mpatches.Patch(facecolor='#fdae61', edgecolor='#1b2a47', label='Ipp-J: E. Palmer Land (61,360 km² ice sheet)'),
    mpatches.Patch(facecolor='#cccccc', edgecolor='#5c2a1e', hatch='///', label='Peripheral Islands (83,791 km² total)')
]
ax.legend(handles=legend_elements, loc='upper left', framealpha=0.95, fontsize=9, title="Delineation Classes")

fig.tight_layout()
fig1_path = os.path.join(FIGURES_DIR, "map1_peninsula_basins_domain.png")
fig.savefig(fig1_path, dpi=300)
plt.close(fig)
print(f"Saved: {fig1_path}")

# -------------------------------------------------------------
# FIGURE 2: Bedmap3 Ice Thickness Map
# -------------------------------------------------------------
print("Generating Map 2: Bedmap3 Ice Thickness...")
thick_path = os.path.join(PROCESSED_DIR, "bedmap3_thickness_peninsula_500m.tif")
mask_path = os.path.join(PROCESSED_DIR, "bedmap3_masks_peninsula_500m.tif")

with rasterio.open(thick_path) as src_thick, rasterio.open(mask_path) as src_mask:
    thickness = src_thick.read(1)
    mask = src_mask.read(1)
    extent = [src_thick.bounds.left, src_thick.bounds.right, src_thick.bounds.bottom, src_thick.bounds.top]

# Filter valid ice pixels (mask: 1=grounded, 3=shelf)
# Thickness is masked where mask is ocean (-9999) or rock (4) or thickness <= 0
valid_ice = (mask == 1) | (mask == 3)
ice_thickness_display = np.where(valid_ice & (thickness > 0), thickness, np.nan)

fig, ax = plt.subplots(figsize=(10, 12), dpi=300)

# Set background to ocean blue
ax.set_facecolor('#dcebf7')

# Plot ice thickness
cmap = plt.cm.viridis.copy()
cmap.set_bad(color='#dcebf7')

im = ax.imshow(ice_thickness_display, extent=extent, origin='upper', cmap=cmap, vmin=0, vmax=2500)

# Overlay basin boundaries
peninsula_gdf.boundary.plot(ax=ax, color='black', linewidth=0.8, alpha=0.7)

# Format coordinates
ax.set_xlim(-2700000, -1400000)
ax.set_ylim(250000, 1950000)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x/1000):,} km"))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f"{int(y/1000):,} km"))
ax.set_xlabel("Polar Stereographic X (m / km)", fontweight='bold')
ax.set_ylabel("Polar Stereographic Y (m / km)", fontweight='bold')
ax.grid(True, linestyle=':', alpha=0.4, color='white')

# Colorbar
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Ice Thickness (m)", fontsize=11, fontweight='bold')

plt.title("Bedmap3 Baseline Ice Thickness (Antarctic Peninsula)\n500 m Native Resolution, BAS / SCAR (EPSG:3031)",
          fontsize=13, fontweight='bold', pad=15)

fig.tight_layout()
fig2_path = os.path.join(FIGURES_DIR, "map2_bedmap3_thickness.png")
fig.savefig(fig2_path, dpi=300)
plt.close(fig)
print(f"Saved: {fig2_path}")

# -------------------------------------------------------------
# FIGURE 3: Bedmap3 Ice Classification and Masks
# -------------------------------------------------------------
print("Generating Map 3: Bedmap3 Ice Classification & Masks...")
fig, ax = plt.subplots(figsize=(10, 12), dpi=300)

# Mask values (Official Bedmap3 publication, Pritchard et al. 2025):
# -9999 = Ocean / Out-of-domain
# 1 = Permanently Grounded Ice Sheet
# 2 = Transiently Grounded Ice Shelf (grounding zone pinning points)
# 3 = Floating Ice Shelf
# 4 = Ice-free Rock Outcrop
mask_mapped = np.zeros_like(mask, dtype=np.int8)
mask_mapped[mask == -9999] = 0  # Ocean
mask_mapped[mask == 1] = 1      # Permanently Grounded Ice
mask_mapped[mask == 2] = 2      # Transiently Grounded Ice Shelf
mask_mapped[mask == 3] = 3      # Floating Ice Shelf
mask_mapped[mask == 4] = 4      # Rock Outcrop

# Colormap for discrete classes
colors = ['#1d3557', '#e0f3f8', '#fdae61', '#74add1', '#8c510a']  # Ocean, Grounded, Transiently Grounded, Shelf, Rock
cmap_discrete = ListedColormap(colors)
norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5], 5)

im = ax.imshow(mask_mapped, extent=extent, origin='upper', cmap=cmap_discrete, norm=norm)

# Overlay basin boundaries
peninsula_gdf.boundary.plot(ax=ax, color='#333333', linewidth=0.7, linestyle='-')

ax.set_xlim(-2700000, -1400000)
ax.set_ylim(250000, 1950000)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x/1000):,} km"))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f"{int(y/1000):,} km"))
ax.set_xlabel("Polar Stereographic X (m / km)", fontweight='bold')
ax.set_ylabel("Polar Stereographic Y (m / km)", fontweight='bold')
ax.grid(True, linestyle=':', alpha=0.3, color='white')

# Legend
class_labels = [
    mpatches.Patch(facecolor='#1d3557', label='Open Ocean / Periphery Water'),
    mpatches.Patch(facecolor='#e0f3f8', edgecolor='gray', label='Permanently Grounded Ice (Class 1)'),
    mpatches.Patch(facecolor='#fdae61', label='Transiently Grounded Ice Shelf (Class 2, 16.0 km²)'),
    mpatches.Patch(facecolor='#74add1', label='Floating Ice Shelves (Class 3, e.g. Larsen C)'),
    mpatches.Patch(facecolor='#8c510a', label='Ice-Free Exposed Rock (Class 4, Nunataks)')
]
ax.legend(handles=class_labels, loc='upper left', framealpha=0.95, fontsize=8.5, title="Scientific Classification")

plt.title("Bedmap3 Geospatial Ice Classification & Surface Mask\nStrict Distinction: Grounded Ice vs. Floating Shelves vs. Rock Outcrops",
          fontsize=12, fontweight='bold', pad=15)

fig.tight_layout()
fig3_path = os.path.join(FIGURES_DIR, "map3_bedmap3_classification_masks.png")
fig.savefig(fig3_path, dpi=300)
plt.close(fig)
print(f"Saved: {fig3_path}")

# -------------------------------------------------------------
# FIGURE 4: Bedmap3 Ice Thickness Uncertainty Grid
# -------------------------------------------------------------
print("Generating Map 4: Bedmap3 Thickness Uncertainty...")
uncert_path = os.path.join(PROCESSED_DIR, "bedmap3_uncertainty_peninsula_500m.tif")

with rasterio.open(uncert_path) as src_u:
    uncertainty = src_u.read(1)

# Mask over ice-covered areas only
uncert_display = np.where(valid_ice & (uncertainty >= 0), uncertainty, np.nan)

fig, ax = plt.subplots(figsize=(10, 12), dpi=300)
ax.set_facecolor('#f0f0f0')

cmap_u = plt.cm.inferno.copy()
cmap_u.set_bad(color='#f0f0f0')

im = ax.imshow(uncert_display, extent=extent, origin='upper', cmap=cmap_u, vmin=0, vmax=350)
peninsula_gdf.boundary.plot(ax=ax, color='cyan', linewidth=0.7, alpha=0.6)

ax.set_xlim(-2700000, -1400000)
ax.set_ylim(250000, 1950000)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x/1000):,} km"))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f"{int(y/1000):,} km"))
ax.set_xlabel("Polar Stereographic X (m / km)", fontweight='bold')
ax.set_ylabel("Polar Stereographic Y (m / km)", fontweight='bold')
ax.grid(True, linestyle=':', alpha=0.3, color='gray')

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Thickness Uncertainty (± m)", fontsize=11, fontweight='bold')

plt.title("Bedmap3 Ice Thickness Uncertainty Distribution\nSpatial Variance Reflecting Airborne Radar Line Density (500 m)",
          fontsize=12, fontweight='bold', pad=15)

fig.tight_layout()
fig4_path = os.path.join(FIGURES_DIR, "map4_bedmap3_thickness_uncertainty.png")
fig.savefig(fig4_path, dpi=300)
plt.close(fig)
print(f"Saved: {fig4_path}")

# -------------------------------------------------------------
# FIGURE 5: Basin Statistical Distribution of Ice Thickness
# -------------------------------------------------------------
print("Generating Map 5: Statistical Distribution Profile...")
from rasterio.mask import mask as rmask

basin_stats = {}
for basin in ['Hp-I', 'I-Ipp', 'Ipp-J']:
    geom = peninsula_gdf[(peninsula_gdf['Basin'] == basin) & (peninsula_gdf['Type'] == 'Ice_sheet')].geometry
    with rasterio.open(thick_path) as src_t, rasterio.open(mask_path) as src_m:
        t_crop, _ = rmask(src_t, geom, crop=True)
        m_crop, _ = rmask(src_m, geom, crop=True)
        t_arr = t_crop[0]
        m_arr = m_crop[0]
        
        # Grounded ice only (mask == 1)
        grounded_thick = t_arr[(m_arr == 1) & (t_arr > 0)]
        basin_stats[basin] = grounded_thick

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Histogram / KDE
bins = np.linspace(0, 2500, 51)
colors_list = ['#2b83ba', '#2ca25f', '#fdae61']

for (b, vals), col in zip(basin_stats.items(), colors_list):
    mean_val = np.mean(vals)
    median_val = np.median(vals)
    ax1.hist(vals, bins=bins, alpha=0.5, color=col, density=True, label=f"{b} (Mean: {mean_val:.0f}m, Med: {median_val:.0f}m)")
    ax1.axvline(median_val, color=col, linestyle='--', linewidth=1.5)

ax1.set_title("Grounded Ice Thickness Frequency Distribution by Basin", fontweight='bold')
ax1.set_xlabel("Ice Thickness (m)", fontweight='bold')
ax1.set_ylabel("Probability Density", fontweight='bold')
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, linestyle=':', alpha=0.5)

# Boxplot
box_data = [basin_stats['I-Ipp'], basin_stats['Hp-I'], basin_stats['Ipp-J']]
box = ax2.boxplot(box_data, patch_artist=True, tick_labels=['I-Ipp\n(Graham Land)', 'Hp-I\n(W. Palmer Land)', 'Ipp-J\n(E. Palmer Land)'])
for patch, color in zip(box['boxes'], ['#2ca25f', '#2b83ba', '#fdae61']):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax2.set_title("Grounded Ice Thickness Quantile Comparisons", fontweight='bold')
ax2.set_ylabel("Ice Thickness (m)", fontweight='bold')
ax2.grid(True, linestyle=':', alpha=0.5)

# Add statistics summary table below or annotation
stats_text = (
    "Basin Hypsometric Summary (Grounded Ice Only):\n"
    f"• Graham Land (I-Ipp):   Mean={np.mean(basin_stats['I-Ipp']):.0f} m | Med={np.median(basin_stats['I-Ipp']):.0f} m | Max={np.max(basin_stats['I-Ipp']):.0f} m\n"
    f"• W. Palmer Land (Hp-I): Mean={np.mean(basin_stats['Hp-I']):.0f} m | Med={np.median(basin_stats['Hp-I']):.0f} m | Max={np.max(basin_stats['Hp-I']):.0f} m\n"
    f"• E. Palmer Land (Ipp-J): Mean={np.mean(basin_stats['Ipp-J']):.0f} m | Med={np.median(basin_stats['Ipp-J']):.0f} m | Max={np.max(basin_stats['Ipp-J']):.0f} m"
)
fig.text(0.12, 0.02, stats_text, fontsize=10, family='monospace', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f7f7f7', edgecolor='#cccccc'))

plt.subplots_adjust(bottom=0.22)
fig5_path = os.path.join(FIGURES_DIR, "map5_peninsula_thickness_distribution.png")
fig.savefig(fig5_path, dpi=300)
plt.close(fig)
print(f"Saved: {fig5_path}")
print("All maps generated successfully!")
