"""
Phase 3.0: Historical Observation Inventory & Timeline Visualization
====================================================================
Generates:
1. reports/tables/historical_dataset_inventory.csv
2. reports/tables/temporal_coverage.csv
3. reports/figures/chart_phase3_satellite_timeline.png
4. reports/figures/diagram_phase3_target_conversion_hierarchy.png
5. reports/figures/chart_phase3_methodology_tradeoffs.png
6. reports/figures/diagram_phase3_validation_split_strategy.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.environ['MPLCONFIGDIR'] = os.path.join(BASE_DIR, 'data', 'processed', '.matplotlib')

def build_tables():
    # 1. Historical Dataset Inventory
    datasets = [
        {
            "Dataset_Name": "MEaSUREs BedMachine Antarctica V4.1",
            "Discipline": "Ice Thickness & Bed Topography",
            "Source_Agency": "NASA / UC Irvine / Dartmouth / NSIDC DAAC",
            "DOI": "10.5067/POJQI54A45HX",
            "Spatial_Domain": "Antarctica South of 53°S",
            "Native_Resolution": "500 m",
            "Temporal_Coverage": "1970–2019 (Nominal Epoch)",
            "Temporal_Frequency": "Static Baseline Raster",
            "Key_Variables": "thickness (ice-eq, m), surface (m), bed (m), firn (FAC, m), mask, source, errbed",
            "Access_Protocol": "NASA Earthdata Login / earthaccess (Protected NetCDF)",
            "Peninsula_Suitability": "Highest (Primary Baseline B; 68.4% IceBoost ML trough resolution)",
            "Known_Limitations": "Static composite; errbed omits spatial correlation and firn density bias"
        },
        {
            "Dataset_Name": "Bedmap3 Gridded Products",
            "Discipline": "Ice Thickness & Bed Topography",
            "Source_Agency": "British Antarctic Survey (BAS) / SCAR / NERC",
            "DOI": "10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2",
            "Spatial_Domain": "Antarctica South of 60°S",
            "Native_Resolution": "500 m",
            "Temporal_Coverage": "1960–2022 (Survey Range)",
            "Temporal_Frequency": "Static Baseline Raster",
            "Key_Variables": "bedmap3_thickness (geom, m), bedmap3_surface (m), bedmap3_bed (m), bedmap3_mask",
            "Access_Protocol": "NERC Polar Data Centre (RAMADDA, Open CC-BY-4.0)",
            "Peninsula_Suitability": "High (Primary Baseline A; direct empirical radar survey compilation)",
            "Known_Limitations": "Ordinary kriging underestimates narrow fjord depths; geometric thickness includes firn"
        },
        {
            "Dataset_Name": "NASA ICESat GLAS Altimetry (GLA12)",
            "Discipline": "Laser Altimetry (Surface Height)",
            "Source_Agency": "NASA GSFC / NSIDC DAAC",
            "DOI": "10.5067/ICESAT/GLAS/DATA209",
            "Spatial_Domain": "Global / Polar (up to 86°S)",
            "Native_Resolution": "~70 m footprints, 170 m along-track",
            "Temporal_Coverage": "2003-02 to 2009-10",
            "Temporal_Frequency": "2–3 campaigns/yr (~33-day campaigns)",
            "Key_Variables": "d_elev (surface elevation, m), geoid, quality flags",
            "Access_Protocol": "NASA Earthdata Login / earthaccess",
            "Peninsula_Suitability": "Moderate (Good for Palmer Land plateaus; high cloud loss and slope error in Graham Land)",
            "Known_Limitations": "Campaign mode (intermittent); steep slope geolocation errors; cloud obscuration"
        },
        {
            "Dataset_Name": "NASA ICESat-2 Land Ice Along-Track (ATL06)",
            "Discipline": "Laser Altimetry (Surface Height)",
            "Source_Agency": "NASA GSFC / NSIDC DAAC",
            "DOI": "10.5067/ATLAS/ATL06.006",
            "Spatial_Domain": "Global / Polar (up to 88°S)",
            "Native_Resolution": "20 m along-track (40 m segments)",
            "Temporal_Coverage": "2018-10 to Present",
            "Temporal_Frequency": "91-day repeat cycle",
            "Key_Variables": "h_li (land ice height, m), h_li_sigma, latitude, longitude",
            "Access_Protocol": "NASA Earthdata Login / earthaccess",
            "Peninsula_Suitability": "High (Exceptional accuracy on ice sheet; high photon count)",
            "Known_Limitations": "Limited to 2018–present (cannot reconstruct pre-2018); cloud cover during winter"
        },
        {
            "Dataset_Name": "NASA ICESat-2 Gridded Height Change (ATL15)",
            "Discipline": "Gridded Altimetry Height Change",
            "Source_Agency": "NASA GSFC / NSIDC DAAC",
            "DOI": "10.5067/O5TW6L64DF6C",
            "Spatial_Domain": "Antarctica",
            "Native_Resolution": "1 km, 3 km, 10 km, 20 km",
            "Temporal_Coverage": "2018-10 to Present",
            "Temporal_Frequency": "Quarterly (3-month) and Annual",
            "Key_Variables": "delta_h (height change, m), dh_dt (m/yr), sigma, ice_mask",
            "Access_Protocol": "NASA Earthdata Login / earthaccess",
            "Peninsula_Suitability": "Highest for Contemporary Benchmark (Direct gridded validation)",
            "Known_Limitations": "Contemporary only (2018–present); does not extend to 1980–2017 historical period"
        },
        {
            "Dataset_Name": "ESA CryoSat-2 SARIn Mode Altimetry",
            "Discipline": "Radar Altimetry (Surface Height)",
            "Source_Agency": "ESA / CPOM / UCL",
            "DOI": "10.5270/CR2-0y7t4d5",
            "Spatial_Domain": "Polar Ice Margins (up to 88°S)",
            "Native_Resolution": "Point soundings (~300 m along-track), 1–2 km gridded dh/dt",
            "Temporal_Coverage": "2010-04 to Present",
            "Temporal_Frequency": "369-day repeat (30-day sub-cycle)",
            "Key_Variables": "elevation (m), dh_dt (elevation rate of change, m/yr)",
            "Access_Protocol": "ESA Open Access / CPOM Portal",
            "Peninsula_Suitability": "High (Bridges the 2010–2018 ICESat/ICESat-2 gap; SARIn mode handles margins)",
            "Known_Limitations": "Radar penetration into firn; dielectric changes from summer surface melting"
        },
        {
            "Dataset_Name": "ITS_LIVE Glacier Velocity Mosaics",
            "Discipline": "Ice Surface Velocity",
            "Source_Agency": "NASA JPL / MEaSUREs / AWS Open Data",
            "DOI": "10.5067/6II6VW8LLWJ7",
            "Spatial_Domain": "Global Land Ice",
            "Native_Resolution": "120 m and 240 m",
            "Temporal_Coverage": "1985 to Present (Optimal: 2013–present)",
            "Temporal_Frequency": "Annual and Monthly mosaics, Zarr data cubes",
            "Key_Variables": "v (m/yr), vx, vy, v_error, count",
            "Access_Protocol": "AWS S3 Open Data (s3://its-live-data/, free, unauthenticated)",
            "Peninsula_Suitability": "Highest for Ice Discharge Gates (Continuous coverage along calving fronts)",
            "Known_Limitations": "Sparse optical coverage in early satellite era (1985–2000); cloud and winter darkness"
        },
        {
            "Dataset_Name": "MEaSUREs Annual Antarctic Ice Velocity",
            "Discipline": "Ice Surface Velocity",
            "Source_Agency": "NASA MEaSUREs / UC Irvine / NSIDC DAAC",
            "DOI": "10.5067/9L5CTA45AZCS",
            "Spatial_Domain": "Antarctic Continent",
            "Native_Resolution": "450 m",
            "Temporal_Coverage": "2005 to 2021 (Annual)",
            "Temporal_Frequency": "Annual Mosaics",
            "Key_Variables": "VX, VY, VV (m/yr), err (m/yr)",
            "Access_Protocol": "NASA Earthdata Login / earthaccess",
            "Peninsula_Suitability": "High (Calibrated InSAR + Landsat feature tracking; mass conservation input)",
            "Known_Limitations": "Annual resolution misses sub-annual surge dynamics; higher error in slow interior ice"
        },
        {
            "Dataset_Name": "RACMO2.3p2 Statistically Downscaled SMB",
            "Discipline": "Surface Mass Balance & Climate",
            "Source_Agency": "IMAU / Utrecht University",
            "DOI": "10.5281/zenodo.5807954",
            "Spatial_Domain": "Antarctica",
            "Native_Resolution": "1 km and 5.5 km (Peninsula model)",
            "Temporal_Coverage": "1979-01 to 2021-12",
            "Temporal_Frequency": "Monthly and Annual",
            "Key_Variables": "smb (mm w.e./yr), precip, runoff, sublimation, snowfall, t2m",
            "Access_Protocol": "Zenodo / Open HTTP (Direct Download)",
            "Peninsula_Suitability": "Highest for Long-Term Historical Reconstruction (43-year continuous series)",
            "Known_Limitations": "Extreme orographic precipitation gradients in Peninsula; requires downscaling"
        },
        {
            "Dataset_Name": "RACMO2.4p1 ERA5-Forced SMB & Climatology",
            "Discipline": "Surface Mass Balance & Climate",
            "Source_Agency": "IMAU / Utrecht University / KNMI",
            "DOI": "10.5281/zenodo.10519398",
            "Spatial_Domain": "Antarctica",
            "Native_Resolution": "11 km (native) / Statistically downscaled",
            "Temporal_Coverage": "1979-01 to 2023-12 (Extending to 2025)",
            "Temporal_Frequency": "Daily, Monthly, Annual",
            "Key_Variables": "smb, precip, sublim, runoff, refreezing, surface_temp",
            "Access_Protocol": "Zenodo / Open HTTP",
            "Peninsula_Suitability": "High (Updated physics and ERA5 reanalysis boundary forcing)",
            "Known_Limitations": "Coarser native grid (11 km) requires high-resolution topographic correction"
        },
        {
            "Dataset_Name": "IMAU-FDM Firn Densification Model",
            "Discipline": "Firn Air Content & Compaction",
            "Source_Agency": "IMAU / Utrecht University",
            "DOI": "10.5194/tc-11-2453-2017",
            "Spatial_Domain": "Antarctica",
            "Native_Resolution": "5.5 km to 27 km downscaled to 500 m",
            "Temporal_Coverage": "1979-01 to 2021-12",
            "Temporal_Frequency": "Daily / Monthly time series and static climatology",
            "Key_Variables": "fac (firn air content depth, m), zs (firn surface height change, m)",
            "Access_Protocol": "IMAU / Zenodo / Embedded in BedMachine V4.1",
            "Peninsula_Suitability": "Indispensable (Converts surface altimetry dh/dt to solid ice volume change)",
            "Known_Limitations": "Empirical compaction parameterization; does not model massive firn collapse/superimposed ice"
        },
        {
            "Dataset_Name": "IMBIE Consensus Mass Balance Assessment",
            "Discipline": "Ice Sheet Mass Balance Intercomparison",
            "Source_Agency": "CPOM / ESA / NASA",
            "DOI": "10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0",
            "Spatial_Domain": "Antarctic Peninsula (APIS) + Continental",
            "Native_Resolution": "Regional Basin Aggregates (APIS)",
            "Temporal_Coverage": "1992-01 to 2020-12 (and 2023 update)",
            "Temporal_Frequency": "Monthly to Annual cumulative mass anomalies",
            "Key_Variables": "dM_dt (mass change rate, Gt/yr), Delta_M (cumulative mass, Gt), sigma",
            "Access_Protocol": "IMBIE Project Portal (Open CSV Download)",
            "Peninsula_Suitability": "Highest for Top-Down Regional Validation (Consensus gold standard)",
            "Known_Limitations": "Regional aggregated mass only (NO spatial grids); GIA uncertainty; cannot be used as direct annual volume"
        },
        {
            "Dataset_Name": "MEaSUREs Antarctic Grounding Line Delineations",
            "Discipline": "Grounding Line & Boundary Migration",
            "Source_Agency": "NASA JPL / UC Irvine / NSIDC DAAC",
            "DOI": "10.5067/D7AKTB54404Z",
            "Spatial_Domain": "Antarctic Coastline",
            "Native_Resolution": "Vector Polylines (~100–500 m precision)",
            "Temporal_Coverage": "1992, 1996, 2000, 2005, 2011, 2016",
            "Temporal_Frequency": "Multi-year epochs",
            "Key_Variables": "grounding_line (geometry), sensor, epoch, uncertainty",
            "Access_Protocol": "NASA Earthdata Login / NSIDC DAAC",
            "Peninsula_Suitability": "High (Constrains grounded area time evolution A_ground(t))",
            "Known_Limitations": "Irregular temporal sampling; cliff-sided fjords exhibit minimal horizontal movement"
        }
    ]
    df_inv = pd.DataFrame(datasets)
    inv_csv = os.path.join(TABLES_DIR, "historical_dataset_inventory.csv")
    df_inv.to_csv(inv_csv, index=False)
    print(f"Saved: {inv_csv}")

    # 2. Temporal Coverage Matrix
    coverage = [
        {"Mission_Dataset": "RACMO2.3p2 / 2.4p1 SMB", "Start_Year": 1979, "End_Year": 2024, "Type": "Climate / Atmospheric Model", "Primary_Variable": "SMB (mm w.e./yr)", "Frequency": "Monthly / Annual", "Peninsula_Utility": "Primary forcing for Input-Output Method"},
        {"Mission_Dataset": "IMAU-FDM Firn Evolution", "Start_Year": 1979, "End_Year": 2021, "Type": "Firn Densification Model", "Primary_Variable": "FAC (m) & dz_firn (m/yr)", "Frequency": "Monthly / Annual", "Peninsula_Utility": "Firn air correction for altimetry and mass"},
        {"Mission_Dataset": "ITS_LIVE Optical/Radar Velocity", "Start_Year": 1985, "End_Year": 2024, "Type": "Satellite Feature Tracking", "Primary_Variable": "Ice Velocity (m/yr)", "Frequency": "Annual / Multi-month", "Peninsula_Utility": "Flux gate discharge calculation"},
        {"Mission_Dataset": "ERS-1 / ERS-2 Altimetry", "Start_Year": 1992, "End_Year": 2003, "Type": "Pulse-limited Radar Altimeter", "Primary_Variable": "dh/dt (m/yr)", "Frequency": "35-day repeat / Multi-year", "Peninsula_Utility": "Early satellite altimetry baseline (IMBIE)"},
        {"Mission_Dataset": "IMBIE Multi-Sensor Consensus", "Start_Year": 1992, "End_Year": 2020, "Type": "Reconciled Mass Balance", "Primary_Variable": "Mass Loss Rate (Gt/yr)", "Frequency": "Monthly / Annual", "Peninsula_Utility": "Top-down regional mass validation"},
        {"Mission_Dataset": "MEaSUREs InSAR Grounding Lines", "Start_Year": 1992, "End_Year": 2016, "Type": "Differential InSAR", "Primary_Variable": "Grounding Zone Position", "Frequency": "Intermittent Epochs", "Peninsula_Utility": "Grounded domain boundary verification"},
        {"Mission_Dataset": "Envisat RA-2 Altimetry", "Start_Year": 2002, "End_Year": 2012, "Type": "Radar Altimeter", "Primary_Variable": "dh/dt (m/yr)", "Frequency": "35-day repeat", "Peninsula_Utility": "Altimetry continuity (IMBIE input)"},
        {"Mission_Dataset": "GRACE Satellite Gravimetry", "Start_Year": 2002, "End_Year": 2017, "Type": "Satellite K-band Ranging Gravimetry", "Primary_Variable": "Gravity / Mass Change (Gt)", "Frequency": "Monthly mascons", "Peninsula_Utility": "Regional mass constraint (coarse resolution)"},
        {"Mission_Dataset": "NASA ICESat GLAS Altimetry", "Start_Year": 2003, "End_Year": 2009, "Type": "Satellite Laser Altimeter", "Primary_Variable": "dh/dt (m/yr)", "Frequency": "2–3 campaigns/yr", "Peninsula_Utility": "High-precision plateau elevation trends"},
        {"Mission_Dataset": "MEaSUREs Annual Velocity Mosaics", "Start_Year": 2005, "End_Year": 2021, "Type": "InSAR / Optical Ice Velocity", "Primary_Variable": "Velocity (m/yr)", "Frequency": "Annual", "Peninsula_Utility": "Standard input to Input-Output Method"},
        {"Mission_Dataset": "ESA CryoSat-2 SARIn Altimetry", "Start_Year": 2010, "End_Year": 2024, "Type": "Interferometric Radar Altimeter", "Primary_Variable": "Elevation & dh/dt (m/yr)", "Frequency": "Sub-monthly / Annual", "Peninsula_Utility": "Continuous marginal ice sheet elevation trends"},
        {"Mission_Dataset": "GRACE Follow-On (GRACE-FO)", "Start_Year": 2018, "End_Year": 2024, "Type": "Laser Ranging Gravimetry", "Primary_Variable": "Gravity / Mass Change (Gt)", "Frequency": "Monthly mascons", "Peninsula_Utility": "Modern regional mass anomaly validation"},
        {"Mission_Dataset": "NASA ICESat-2 (ATL06/ATL15)", "Start_Year": 2018, "End_Year": 2024, "Type": "Multi-beam Photon-Counting Lidar", "Primary_Variable": "Elevation & Gridded dh/dt", "Frequency": "91-day repeat / Quarterly", "Peninsula_Utility": "Definitive contemporary benchmark (high-precision)"}
    ]
    df_cov = pd.DataFrame(coverage)
    cov_csv = os.path.join(TABLES_DIR, "temporal_coverage.csv")
    df_cov.to_csv(cov_csv, index=False)
    print(f"Saved: {cov_csv}")

def generate_figures():
    # -------------------------------------------------------------------------
    # FIGURE 1: Satellite & Climate Mission Timeline (1979–2026)
    # -------------------------------------------------------------------------
    print("Generating Figure 1: Historical Timeline...")
    df_cov = pd.read_csv(os.path.join(TABLES_DIR, "temporal_coverage.csv"))
    
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    
    categories = {
        "Climate / Atmospheric Model": "#0284c7",
        "Firn Densification Model": "#0d9488",
        "Satellite Feature Tracking": "#d97706",
        "Pulse-limited Radar Altimeter": "#8b5cf6",
        "Reconciled Mass Balance": "#ec4899",
        "Differential InSAR": "#64748b",
        "Radar Altimeter": "#7c3aed",
        "Satellite K-band Ranging Gravimetry": "#b45309",
        "Satellite Laser Altimeter": "#059669",
        "InSAR / Optical Ice Velocity": "#ea580c",
        "Interferometric Radar Altimeter": "#6366f1",
        "Laser Ranging Gravimetry": "#92400e",
        "Multi-beam Photon-Counting Lidar": "#10b981"
    }
    
    y_positions = np.arange(len(df_cov))
    
    for i, row in df_cov.iterrows():
        start = row['Start_Year']
        end = row['End_Year']
        m_type = row['Type']
        color = categories.get(m_type, '#475569')
        
        ax.barh(i, end - start, left=start, height=0.55, color=color, edgecolor='#0f172a', alpha=0.9)
        
        # Add text inside or beside bar
        label_text = f"{row['Mission_Dataset']} ({start}–{end})"
        if (end - start) > 12:
            ax.text(start + 0.8, i, label_text, va='center', ha='left', fontsize=8.5, fontweight='bold', color='#ffffff')
        else:
            ax.text(end + 0.6, i, label_text, va='center', ha='left', fontsize=8.5, fontweight='bold', color='#1e293b')
            
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df_cov['Mission_Dataset'], fontsize=9, fontweight='bold')
    ax.invert_yaxis()
    
    ax.set_xlim(1975, 2030)
    ax.set_xlabel("Observation Year", fontsize=11, fontweight='bold')
    ax.set_title("Timeline of Satellite & Climate Missions Across the Antarctic Peninsula (1979–2026)\nMapping Observational Coverage for Historical Ice-Volume Reconstruction", fontsize=13, fontweight='bold', pad=12)
    
    # Highlight key milestone vertical spans
    ax.axvspan(1979, 1992, color='#f1f5f9', alpha=0.6, label='Pre-Altimetry ERA5 / RACMO Era (1979–1992)')
    ax.axvspan(1992, 2002, color='#e0f2fe', alpha=0.4, label='Early Satellite Altimetry & ERS Era (1992–2002)')
    ax.axvspan(2002, 2018, color='#fef3c7', alpha=0.4, label='GRACE / ICESat / CryoSat-2 Era (2002–2018)')
    ax.axvspan(2018, 2026, color='#dcfce7', alpha=0.5, label='Modern High-Precision ICESat-2 / GRACE-FO Era (2018–2026)')
    
    ax.grid(True, linestyle=':', alpha=0.5, axis='x')
    ax.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "chart_phase3_satellite_timeline.png")
    fig.savefig(fig1_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {fig1_path}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Observation Hierarchy & Target Conversion Diagram
    # -------------------------------------------------------------------------
    print("Generating Figure 2: Observation Hierarchy & Conversion Diagram...")
    fig, ax = plt.subplots(figsize=(13, 9), dpi=300)
    ax.axis('off')
    
    # Draw boxes
    def draw_box(x, y, w, h, title, subtitle, color, ec='#0f172a'):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", fc=color, ec=ec, lw=1.5)
        ax.add_patch(box)
        ax.text(x + w/2.0, y + h*0.7, title, ha='center', va='center', fontsize=10, fontweight='bold', color='#0f172a')
        ax.text(x + w/2.0, y + h*0.3, subtitle, ha='center', va='center', fontsize=8, color='#334155', multialignment='center')
        return box
        
    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color='#1e293b', lw=2.0, shrinkA=5, shrinkB=5))
        if label:
            mx, my = (x1 + x2)/2.0, (y1 + y2)/2.0
            ax.text(mx, my + 0.025, label, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#94a3b8", alpha=0.9))

    # Column 1: Observational Inputs
    b_alt = draw_box(0.05, 0.72, 0.25, 0.18, "Observational Quantity C\nSurface Elevation Change (dh/dt)", "ICESat, ICESat-2, CryoSat-2\nUnits: [m / yr]", "#dbeafe")
    b_smb = draw_box(0.05, 0.40, 0.25, 0.18, "Observational Quantity D1\nSurface Mass Balance (SMB)", "RACMO2.3p2 / 2.4p1 Models\nUnits: [mm w.e./yr] -> [Gt/yr]", "#ccfbf1")
    b_dis = draw_box(0.05, 0.08, 0.25, 0.18, "Observational Quantity D2\nIce Discharge Gate Flux (D)", "ITS_LIVE, MEaSUREs Velocity × H\nUnits: [Gt / yr]", "#fed7aa")

    # Column 2: Correction & Synthesis Engines
    b_firn = draw_box(0.38, 0.72, 0.25, 0.18, "Firn Air & GIA Correction Engine", "Subtract dFAC/dt (IMAU-FDM)\nSubtract v_GIA (W12a / IJ05_R2)\nAccount for snow density rho_firn", "#e0e7ff")
    b_iom = draw_box(0.38, 0.24, 0.25, 0.24, "Input-Output Mass Continuity Engine\n(IOM / Lagrangian Budget)", "dM/dt = SMB(t) - D(t)\nContinuous 1979–2024 annual series\nGate-specific flux divergence", "#fef08a")

    # Column 3: Intermediate Mass Target
    b_mass = draw_box(0.70, 0.24, 0.25, 0.24, "Intermediate Target B\nGrounded Ice Mass Change (dM/dt)", "IMBIE & GRACE/GRACE-FO\nMass rate: [Gt / yr]\nCumulative anomaly: Delta M [Gt]", "#fbcfe8")

    # Column 4: Primary Prediction Target (Center Top)
    b_target = draw_box(0.68, 0.68, 0.28, 0.24, "PRIMARY TARGET A\nGrounded Ice-Equivalent Volume (V_ice_eq)", "V_ice_eq(t) = sum(H_ice_eq * A_ground)\nUnits: [km³]\nPure Solid Ice (rho_i = 917 kg/m³)", "#bbf7d0", ec="#16a34a")

    # Connect with arrows and formulas
    draw_arrow(0.30, 0.81, 0.38, 0.81, "Geodetic Altimetry")
    draw_arrow(0.30, 0.49, 0.38, 0.40, "+ Input (Accumulation)")
    draw_arrow(0.30, 0.17, 0.38, 0.32, "- Output (Discharge)")
    
    draw_arrow(0.63, 0.81, 0.68, 0.81, "dV_ice_eq = int(dh - dFAC - GIA)dA")
    draw_arrow(0.63, 0.36, 0.70, 0.36, "dM/dt = SMB - D")
    draw_arrow(0.82, 0.48, 0.82, 0.68, "dV_ice_eq/dt = (1 / rho_i) * dM/dt\n(1 Gt = 1.0905 km³)")

    ax.set_title("Physical Observation Hierarchy & Target Conversion Framework\nDecoupling Surface Height (dh/dt), Mass Anomalies (dM/dt), and Solid Ice-Equivalent Volume (V_ice_eq)", fontsize=13, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "diagram_phase3_target_conversion_hierarchy.png")
    fig.savefig(fig2_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {fig2_path}")

    # -------------------------------------------------------------------------
    # FIGURE 3: Methodology Comparison & Trade-off Matrix
    # -------------------------------------------------------------------------
    print("Generating Figure 3: Methodology Comparison...")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    
    methods = [
        "Input-Output Method (IOM)\n[RACMO SMB - Velocity Flux]",
        "Repeat-Track Laser Altimetry\n[ICESat & ICESat-2]",
        "Interferometric Radar Altimetry\n[CryoSat-2 SARIn]",
        "Satellite Gravimetry\n[GRACE & GRACE-FO Mascons]",
        "Reconciled Multi-Sensor Consensus\n[IMBIE Synthesis]"
    ]
    
    # Attributes: [Temporal Coverage Score (0-10), Spatial Resolution Score (0-10), Peninsula Alpine Suitability (0-10), Annual Time-Series Continuity (0-10)]
    scores = np.array([
        [10.0, 8.5, 9.0, 10.0],  # IOM
        [5.0, 9.5, 6.5, 5.0],   # Laser Altimetry
        [7.0, 8.0, 7.5, 7.0],   # CryoSat-2
        [6.5, 2.0, 4.0, 8.0],   # GRACE
        [8.0, 3.0, 7.0, 7.5]    # IMBIE
    ])
    
    x = np.arange(len(methods))
    width = 0.2
    
    ax.bar(x - 1.5*width, scores[:, 0], width=width, label='Temporal Coverage (1979–Present)', color='#0284c7')
    ax.bar(x - 0.5*width, scores[:, 1], width=width, label='Spatial Resolution (< 1 km)', color='#10b981')
    ax.bar(x + 0.5*width, scores[:, 2], width=width, label='Peninsula Alpine Suitability', color='#f59e0b')
    ax.bar(x + 1.5*width, scores[:, 3], width=width, label='Annual Time-Series Continuity', color='#8b5cf6')
    
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontweight='bold', fontsize=9)
    ax.set_ylabel("Methodological Evaluation Score (0–10)", fontweight='bold', fontsize=10)
    ax.set_ylim(0, 12)
    ax.set_title("Comparative Evaluation of Historical Reconstruction Methodologies\nSuitability for Antarctic Peninsula Mainland Basins (Hp-I, I-Ipp, Ipp-J)", fontsize=13, fontweight='bold', pad=12)
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.95)
    ax.grid(True, linestyle=':', alpha=0.5, axis='y')
    
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "chart_phase3_methodology_tradeoffs.png")
    fig.savefig(fig3_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {fig3_path}")

    # -------------------------------------------------------------------------
    # FIGURE 4: Chronological Train / Validation / Test Splitting Strategy
    # -------------------------------------------------------------------------
    print("Generating Figure 4: Validation Splitting Strategy...")
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    
    # 3 partitions:
    # Train: 1979 - 2010 (32 years)
    # Val:   2011 - 2017 (7 years)
    # Test:  2018 - 2024 (7 years)
    
    p1 = patches.Rectangle((1979, 0.3), 32, 0.4, color='#3b82f6', alpha=0.85, ec='#1e3a8a', lw=1.5)
    p2 = patches.Rectangle((2011, 0.3), 7, 0.4, color='#f59e0b', alpha=0.85, ec='#b45309', lw=1.5)
    p3 = patches.Rectangle((2018, 0.3), 7, 0.4, color='#10b981', alpha=0.85, ec='#047857', lw=1.5)
    
    ax.add_patch(p1)
    ax.add_patch(p2)
    ax.add_patch(p3)
    
    ax.text(1979 + 16, 0.5, "TRAINING PARTITION (1979–2010)\n32 Years • Historical Reanalysis & Early Altimetry\nCalibrates baseline dynamics & SMB forcing",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#ffffff')
    
    ax.text(2011 + 3.5, 0.5, "VALIDATION (2011–2017)\n7 Years • CryoSat-2 SARIn &\nLandsat-8 / Sentinel-1\nHyperparameter tuning",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')
    
    ax.text(2018 + 3.5, 0.5, "TEST BENCHMARK (2018–2024)\n7 Years • ICESat-2 (ATL15) &\nGRACE-FO Modern Gold Standard\nIndependent Out-of-Sample Verification",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')
    
    ax.set_xlim(1976, 2027)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("Calendar Year", fontsize=11, fontweight='bold')
    ax.set_title("Chronological Train / Validation / Test Splitting Framework for Future ML\nStrictly Precludes Temporal Leakage; Preserves Out-of-Sample Modern Benchmark", fontsize=13, fontweight='bold', pad=12)
    
    # Add annotation below explaining no shuffling
    ax.text(2002, 0.12, "CRITICAL PRINCIPLE: Never perform random cross-validation on time-series glaciological data.\nAutocorrelation across successive years guarantees severe data leakage if randomly shuffled.",
            ha='center', va='center', fontsize=9, fontstyle='italic', color='#dc2626',
            bbox=dict(boxstyle="round,pad=0.3", fc="#fee2e2", ec="#ef4444", alpha=0.9))
    
    ax.grid(True, linestyle=':', alpha=0.5, axis='x')
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "diagram_phase3_validation_split_strategy.png")
    fig.savefig(fig4_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {fig4_path}")

if __name__ == "__main__":
    build_tables()
    generate_figures()
    print("Phase 3.0 Inventory & Visualization Generation Complete.")

