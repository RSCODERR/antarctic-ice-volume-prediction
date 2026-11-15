"""
Phase 3.1B: Historical Reconstruction Methodology Design
========================================================
Generates all 5 required tables and 3 publication-quality architecture/workflow diagrams:
- reports/tables/epoch_methodology_matrix.csv
- reports/tables/reconstruction_provenance_matrix.csv
- reports/tables/domain_implementation_matrix.csv
- reports/tables/gia_model_comparison.csv
- reports/tables/uncertainty_budget_design.csv
- reports/figures/diagram_phase3_1b_data_flow_architecture.png
- reports/figures/diagram_phase3_1b_correction_sequence.png
- reports/figures/diagram_phase3_1b_uncertainty_propagation.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.environ['MPLCONFIGDIR'] = os.path.join(PROCESSED_DIR, '.matplotlib')

# -------------------------------------------------------------------------
# 1. Table: epoch_methodology_matrix.csv
# -------------------------------------------------------------------------
def generate_epoch_methodology_matrix():
    data = [
        {
            "Epoch": "Epoch 1: 1979–1999",
            "Time_Span": "1979-01-01 to 1999-12-31 (21 years)",
            "Methodological_Characterization": "Model-assisted reconstruction with alternative discharge parameterizations",
            "Primary_Data_Streams": "RACMO2.3p2 / 2.4p1 downscaled SMB (ERA-forced), ERS-1/2 InSAR (1996 snapshot), Radarsat (1997 snapshot)",
            "Provenance_Breakdown": "SMB: Model output (ERA-forced). Discharge: Reconstructed / Parameterized estimate (NOT directly observed). Altimetry/Gravimetry: Non-existent.",
            "Observational_Completeness_%": 18.5,
            "Discharge_Methodology": "Input-Output Method with parameterized discharge scenarios anchored to 1996 InSAR baseline and balance flux",
            "Discharge_Scenarios_Defined": "Low (pre-collapse steady-state D = SMB_1979-1989), Central (calibrated IOM with 1996 InSAR + gradual pre-collapse adjustment), High (accelerated late-90s discharge scaling with early Larsen A opening)",
            "Altimetry_Gravimetry_Role": "None (pre-satellite altimetry/gravimetry era; cannot provide independent cross-check)",
            "Dominant_Uncertainty_Type": "Scenario uncertainty (unmeasured historical discharge) and model uncertainty (ERA reanalysis forcing)",
            "Validation_Anchor": "Regional IMBIE 2026 reconciled total mass balance (APIS aggregate benchmark; +/- 25 Gt/yr uncertainty)"
        },
        {
            "Epoch": "Epoch 2: 2000–2013",
            "Time_Span": "2000-01-01 to 2013-12-31 (14 years)",
            "Methodological_Characterization": "Multi-sensor constrained reconstruction with intermediate spatial/temporal limitations",
            "Primary_Data_Streams": "RACMO2.3p2/2.4p1 SMB, ICESat-1 GLAS laser altimetry, GRACE RL06 mascons, intermittent Envisat/ALOS/Landsat-7 velocity, early CryoSat-2 (2010–)",
            "Provenance_Breakdown": "SMB: Model output. Velocity: Interpolated / Reconstructed estimate (sporadic observations, heavy cloud gaps in I-Ipp). Altimetry: Direct observation (campaign-mode; track spacing 10–30 km; slope dropouts). Gravimetry: Regional constraint (mascon ~300 km resolution; cannot resolve individual basins).",
            "Observational_Completeness_%": 52.4,
            "Discharge_Methodology": "Surge-tracking IOM over Larsen B tributaries (Crane, Green, Hektoria) combined with multi-year satellite elevation/mass balance constraints",
            "Discharge_Scenarios_Defined": "Post-collapse transient decay parameterizations for Larsen B glaciers; balance-flux scaling elsewhere",
            "Altimetry_Gravimetry_Role": "Multi-year boundary constraint. GRACE provides integrated Peninsula sector mass rate; ICESat-1 provides repeat-track dh/dt on smooth plateau ice (slopes < 2°)",
            "Dominant_Uncertainty_Type": "Measurement uncertainty (ICESat slope geolocation errors, GRACE spatial leakage) and structural GIA uncertainty",
            "Validation_Anchor": "IMBIE 2026 reconciled record (+/- 14 Gt/yr) and independent ICESat-1 / GRACE regional mass loss rates"
        },
        {
            "Epoch": "Epoch 3: 2014–2024",
            "Time_Span": "2014-01-01 to 2024-12-31 (11 years)",
            "Methodological_Characterization": "Observation-rich reconstruction with remaining observational and geophysical uncertainties",
            "Primary_Data_Streams": "Sentinel-1A/B SAR 6-to-12 day velocity, Landsat-8/9 feature tracking, CryoSat-2 SARIn radar altimetry, ICESat-2 (ATL15) laser altimetry, GRACE-FO mascons, RACMO2.4p1",
            "Provenance_Breakdown": "SMB: Model output (ERA5-forced). Velocity: Direct observation (continuous annual/seasonal). Altimetry: Direct observation (high-density SARIn & ATLAS lidar). Gravimetry: Regional constraint (GRACE-FO mascons).",
            "Observational_Completeness_%": 94.6,
            "Discharge_Methodology": "Empirical annual Input-Output flux-gate integration across all verified outlet glaciers using observed velocity fields",
            "Discharge_Scenarios_Defined": "Directly observed discharge time series with observational error bands (no parameterization scenarios required)",
            "Altimetry_Gravimetry_Role": "Tri-sensor synthesis: Altimetry (ATL15 + CryoSat-2) independently validates IOM volume loss rates; GRACE-FO validates total mass loss rate",
            "Dominant_Uncertainty_Type": "Structural uncertainty (Bedmap3 vs BedMachine thickness differences), radar penetration biases, and slab-window GIA corrections",
            "Validation_Anchor": "IMBIE 2026 consensus, ICESat-2 ATL15 gridded dh/dt, and Sentinel-1 annual grounding-line discharge gates"
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "epoch_methodology_matrix.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df

# -------------------------------------------------------------------------
# 2. Table: reconstruction_provenance_matrix.csv
# -------------------------------------------------------------------------
def generate_reconstruction_provenance_matrix():
    data = [
        # Atmospheric / SMB
        {"Variable": "smb_monthly", "Description": "Spatially gridded monthly surface mass balance", "Epoch_1979_1999": "Model output (RACMO2.3p2 / ERA-Interim)", "Epoch_2000_2013": "Model output (RACMO2.3p2 / ERA5)", "Epoch_2014_2024": "Model output (RACMO2.4p1 / ERA5)", "Primary_Sensors_Models": "RACMO RCM forced by ECMWF reanalysis", "Physical_Units": "mm w.e./yr (kg m-2 yr-1)", "Basin_Resolution": "1 km downscaled EPSG:3031", "Limitation_or_Assumption": "Uncertainty ~15%; sensitive to coastal topography downscaling"},
        {"Variable": "fac_evolution", "Description": "Firn air content time series (dFAC/dt)", "Epoch_1979_1999": "Model output (IMAU-FDM)", "Epoch_2000_2013": "Model output (IMAU-FDM)", "Epoch_2014_2024": "Model output (IMAU-FDM)", "Primary_Sensors_Models": "IMAU Firn Densification Model", "Physical_Units": "m firn air / yr", "Basin_Resolution": "500 m grid", "Limitation_or_Assumption": "Assumes tipping-bucket refreezing; does not resolve ice slab impermeability"},
        
        # Ice Velocity & Discharge
        {"Variable": "ice_surface_velocity", "Description": "Annual surface velocity fields on glacier trunks", "Epoch_1979_1999": "Assumption / Parameterized estimate (1996 InSAR snapshot)", "Epoch_2000_2013": "Interpolated or gap-filled estimate (Landsat-7/Envisat/ALOS)", "Epoch_2014_2024": "Direct observation (Sentinel-1 SAR + Landsat-8/9)", "Primary_Sensors_Models": "ITS_LIVE, MEaSUREs, ERS-1/2, Sentinel-1", "Physical_Units": "m/yr", "Basin_Resolution": "240 m / 450 m grids", "Limitation_or_Assumption": "Pre-2014 has >70% annual gaps in I-Ipp; cannot resolve pre-2014 annual dynamics without models"},
        {"Variable": "flux_gate_discharge", "Description": "Solid ice dynamic discharge through flux gates (D)", "Epoch_1979_1999": "Reconstructed estimate (Low/Central/High scenarios)", "Epoch_2000_2013": "Reconstructed estimate (Surge tracking + interpolation)", "Epoch_2014_2024": "Direct observation (Empirical gate integration)", "Primary_Sensors_Models": "IOM gate integration (v_perp * H_ice_eq * width * alpha)", "Physical_Units": "Gt/yr & km3/yr", "Basin_Resolution": "8 gate systems (Hp-I, I-Ipp, Ipp-J)", "Limitation_or_Assumption": "Depth-averaged factor alpha (0.95 sliding, 0.80 shearing); thickness product choice"},
        
        # Altimetry & Height Change
        {"Variable": "surface_height_change (dh/dt)", "Description": "Grounded surface elevation rate of change", "Epoch_1979_1999": "Non-existent", "Epoch_2000_2013": "Direct observation (ICESat campaigns; smooth slopes < 2°)", "Epoch_2014_2024": "Direct observation (CryoSat-2 SARIn + ICESat-2 ATL15)", "Primary_Sensors_Models": "GLAS, SIRAL, ATLAS", "Physical_Units": "m/yr", "Basin_Resolution": "Point soundings / 1 km gridded", "Limitation_or_Assumption": "Ku-band radar penetration (0.5–4.5 m); ICESat-1 steep slope failure; track gaps"},
        
        # Gravimetry & Total Mass
        {"Variable": "regional_mass_rate (dM/dt)", "Description": "Integrated sector-scale mass anomaly rate", "Epoch_1979_1999": "Non-existent", "Epoch_2000_2013": "Regional constraint (GRACE mascons ~300 km)", "Epoch_2014_2024": "Regional constraint (GRACE-FO mascons ~300 km)", "Primary_Sensors_Models": "GRACE / GRACE-FO K-band Ranging", "Physical_Units": "Gt/yr", "Basin_Resolution": "Whole Antarctic Peninsula Sector (APIS)", "Limitation_or_Assumption": "Cannot resolve individual basins (Hp-I vs I-Ipp); leakage across ocean/ice shelf"},
        
        # Regional Consensus Benchmark
        {"Variable": "imbie_reconciled_mb", "Description": "Reconciled multi-method aggregate mass balance", "Epoch_1979_1999": "Regional constraint (IOM-dominated synthesis)", "Epoch_2000_2013": "Regional constraint (IOM + Altimetry + GRACE)", "Epoch_2014_2024": "Regional constraint (Multi-satellite consensus)", "Primary_Sensors_Models": "Otosaka et al. (2026) IMBIE-3 v1.0", "Physical_Units": "Gt/yr & Cumulative Gt", "Basin_Resolution": "Regional APIS scalar series (NOT basin-level)", "Limitation_or_Assumption": "Benchmark for regional sum ONLY; must NOT be treated as basin ground truth"},
        
        # Geophysical Corrections
        {"Variable": "gia_bedrock_uplift (v_GIA)", "Description": "Solid Earth viscoelastic rebound rate", "Epoch_1979_1999": "Model output (Regional slab window viscoelastic model)", "Epoch_2000_2013": "Model output (GPS-constrained regional solution)", "Epoch_2014_2024": "Model output (GPS-constrained regional solution)", "Primary_Sensors_Models": "Nield et al. (2014) / Wolstencroft et al. (2015)", "Physical_Units": "mm/yr uplift", "Basin_Resolution": "10 km to 20 km regional grid", "Limitation_or_Assumption": "Low-viscosity asthenosphere (10^18 Pa s); highly heterogeneous (+2 to +15 mm/yr)"},
        {"Variable": "elastic_rebound (v_elastic)", "Description": "Instantaneous lithospheric rebound to contemporary unloading", "Epoch_1979_1999": "Assumption (Near-zero pre-collapse)", "Epoch_2000_2013": "Model output (Green's function convolution with ice loss)", "Epoch_2014_2024": "Model output (Green's function convolution with ice loss)", "Primary_Sensors_Models": "Regional elastic loading models", "Physical_Units": "mm/yr uplift", "Basin_Resolution": "5 km to 10 km grid", "Limitation_or_Assumption": "Coupled to contemporary discharge; concentrated near Larsen A/B outlets"},
        
        # Annual Output Time Series
        {"Variable": "annual_volume_change_DomainA", "Description": "Reconstructed annual grounded ice-eq volume trajectory", "Epoch_1979_1999": "Reconstructed estimate (Model-assisted IOM synthesis)", "Epoch_2000_2013": "Reconstructed estimate (Multi-sensor reconciled synthesis)", "Epoch_2014_2024": "Reconstructed estimate (Observation-rich empirical synthesis)", "Primary_Sensors_Models": "dV_ice_eq/dt = (SMB - D) / 0.917", "Physical_Units": "km3/yr & Cumulative km3", "Basin_Resolution": "Basins Hp-I, I-Ipp, Ipp-J on Domain A", "Limitation_or_Assumption": "Preserves Bedmap3 and BedMachine baselines separately; no baseline averaging"}
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "reconstruction_provenance_matrix.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df

# -------------------------------------------------------------------------
# 3. Table: domain_implementation_matrix.csv
# -------------------------------------------------------------------------
def generate_domain_implementation_matrix():
    data = [
        {
            "Domain_Category": "Domain A: Common Grounded Footprint",
            "Spatial_Definition": "Cells classified as grounded ice in BOTH Bedmap3 (mask == 1) and BedMachine (mask == 2)",
            "Cell_Count": 863979,
            "Projected_Area_km2": 216062.2,
            "Percentage_of_Peninsula_Grounded_%": 97.52,
            "Mean_BM3_Thickness_m": 622.7,
            "Mean_BM4_Thickness_m": 656.0,
            "BM3_Ice_Eq_Volume_km3": 133497.6,
            "BM4_Ice_Eq_Volume_km3": 140702.5,
            "Structural_Discrepancy_km3": 7204.9,
            "Dynamic_Reconstruction_Eligibility": "Fully Eligible (Primary Dynamic Reconstruction Target)",
            "Volume_Trajectory_Rule": "dV_ice_eq/dt(t) = (SMB_A(t) - D_A(t)) / 0.917. Anchored to dual baselines (133,497.6 vs 140,702.5 km3).",
            "Uncertainty_Treatment": "Propagate SMB, velocity, flux-gate, and firn compaction errors; preserve +7,204.9 km3 as structural baseline divergence"
        },
        {
            "Domain_Category": "Domain B1: Bedmap3-Only Candidate Rock / Nunataks",
            "Spatial_Definition": "Bedmap3 mask == 1 (grounded) BUT BedMachine mask == 1 (ice-free land / exposed rock nunatak)",
            "Cell_Count": 18628,
            "Projected_Area_km2": 4608.5,
            "Percentage_of_Peninsula_Grounded_%": 2.08,
            "Mean_BM3_Thickness_m": 141.1,
            "Mean_BM4_Thickness_m": 0.0,
            "BM3_Ice_Eq_Volume_km3": 620.3,
            "BM4_Ice_Eq_Volume_km3": 0.0,
            "Structural_Discrepancy_km3": -620.3,
            "Dynamic_Reconstruction_Eligibility": "Ineligible for Dynamic Discharge (Evaluated Under Alternative Hypotheses)",
            "Volume_Trajectory_Rule": "Do NOT apply common-domain dynamic thinning. Hypotheses: (H1) Bare rock (dH/dt = 0, H=0); (H2) Stagnant ice mantle / hanging cirque (dH/dt = SMB_local / 0.917); (H3) Mask boundary uncertainty (+/- 620.3 km3 static offset).",
            "Uncertainty_Treatment": "Classified as structural mask uncertainty (+620.3 km3). Never combined into Domain A dynamic flux gates."
        },
        {
            "Domain_Category": "Domain B2: Bedmap3-Only Floating Shelf Classification",
            "Spatial_Definition": "Bedmap3 mask == 1 (grounded) BUT BedMachine mask == 3 (floating ice shelf)",
            "Cell_Count": 2053,
            "Projected_Area_km2": 506.4,
            "Percentage_of_Peninsula_Grounded_%": 0.23,
            "Mean_BM3_Thickness_m": 273.4,
            "Mean_BM4_Thickness_m": 0.0,
            "BM3_Ice_Eq_Volume_km3": 133.8,
            "BM4_Ice_Eq_Volume_km3": 0.0,
            "Structural_Discrepancy_km3": -133.8,
            "Dynamic_Reconstruction_Eligibility": "Strictly Excluded from Grounded Target",
            "Volume_Trajectory_Rule": "Confirmed floating ice shelf under hydrostatic equilibrium; excluded from grounded ice volume target. dV_grounded/dt = 0.",
            "Uncertainty_Treatment": "Excluded from grounded ice-equivalent target. Grounding line migration tracked separately if retreat occurs."
        },
        {
            "Domain_Category": "Domain B3: Bedmap3-Only Coastal Ocean / Waterline",
            "Spatial_Definition": "Bedmap3 mask == 1 (grounded) BUT BedMachine mask == 0 (open water / coastal fjord)",
            "Cell_Count": 1554,
            "Projected_Area_km2": 376.6,
            "Percentage_of_Peninsula_Grounded_%": 0.17,
            "Mean_BM3_Thickness_m": 85.0,
            "Mean_BM4_Thickness_m": 0.0,
            "BM3_Ice_Eq_Volume_km3": 30.4,
            "BM4_Ice_Eq_Volume_km3": 0.0,
            "Structural_Discrepancy_km3": -30.4,
            "Dynamic_Reconstruction_Eligibility": "Strictly Excluded from Grounded Target",
            "Volume_Trajectory_Rule": "Confirmed open water / fjord / calved ice tongue; excluded from grounded target. dV_grounded/dt = 0.",
            "Uncertainty_Treatment": "Excluded from grounded ice-equivalent target. Represents coastal waterline clipping artifact."
        },
        {
            "Domain_Category": "Domain C: BedMachine-Only Grounded Footprint",
            "Spatial_Definition": "BedMachine mask == 2 (grounded) BUT Bedmap3 NOT grounded",
            "Cell_Count": 0,
            "Projected_Area_km2": 0.0,
            "Percentage_of_Peninsula_Grounded_%": 0.0,
            "Mean_BM3_Thickness_m": 0.0,
            "Mean_BM4_Thickness_m": 0.0,
            "BM3_Ice_Eq_Volume_km3": 0.0,
            "BM4_Ice_Eq_Volume_km3": 0.0,
            "Structural_Discrepancy_km3": 0.0,
            "Dynamic_Reconstruction_Eligibility": "Null Domain (Strict Subset Confirmed)",
            "Volume_Trajectory_Rule": "Empty set. BedMachine grounded domain is a mathematically strict subset of Bedmap3 grounded domain.",
            "Uncertainty_Treatment": "None (zero cells verified across all three basins)."
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "domain_implementation_matrix.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df

# -------------------------------------------------------------------------
# 4. Table: gia_model_comparison.csv
# -------------------------------------------------------------------------
def generate_gia_model_comparison():
    data = [
        {
            "Model_Name": "W12 / W12a",
            "Reference": "Whitehouse et al. (2012, Geophys. J. Int.)",
            "Model_Type": "Continental 1D Viscoelastic (Post-LGM)",
            "Viscosity_Structure": "Uniform upper mantle: 2.0e20 Pa s; lower mantle: 1.0e21 Pa s",
            "Lithospheric_Thickness_km": 120.0,
            "Northern_Peninsula_Uplift_mm_yr": "+1.5 to +3.0 mm/yr",
            "Southern_Palmer_Uplift_mm_yr": "+1.0 to +2.0 mm/yr",
            "Spatial_Gradient_Character": "Very gentle gradient; cannot reproduce localized GPS uplift",
            "Time_Dependence": "Steady linear rate assumed over multi-decadal satellite era",
            "Peninsula_Geographical_Validity": "Low in Northern Peninsula (fails to capture slab window asthenosphere); moderate in Palmer Land",
            "Altimetric_Volume_Impact_km3_yr": "-0.3 to -0.6 km3/yr (apparent uplift correction)",
            "Gravimetric_Mass_Impact_Gt_yr": "+2 to +4 Gt/yr mass correction",
            "Methodological_Recommendation": "Retained as continental baseline sensitivity scenario; NOT recommended as primary regional GIA"
        },
        {
            "Model_Name": "ICE-6G_C (VM5a)",
            "Reference": "Peltier et al. (2015, JGR Solid Earth)",
            "Model_Type": "Global 1D Viscoelastic (Post-LGM)",
            "Viscosity_Structure": "1D VM5a viscosity profile (upper mantle ~5.0e20 Pa s)",
            "Lithospheric_Thickness_km": 90.0,
            "Northern_Peninsula_Uplift_mm_yr": "+1.0 to +2.5 mm/yr",
            "Southern_Palmer_Uplift_mm_yr": "+0.5 to +1.5 mm/yr",
            "Spatial_Gradient_Character": "Broad continental wavelength; zero local dynamic response",
            "Time_Dependence": "Steady linear rate",
            "Peninsula_Geographical_Validity": "Low in Antarctic Peninsula; ignores regional tectonics and Cenozoic slab window",
            "Altimetric_Volume_Impact_km3_yr": "-0.2 to -0.5 km3/yr",
            "Gravimetric_Mass_Impact_Gt_yr": "+1 to +3 Gt/yr mass correction",
            "Methodological_Recommendation": "Alternative global sensitivity scenario only"
        },
        {
            "Model_Name": "IJ05_RII",
            "Reference": "Ivins et al. (2013, JGR Solid Earth)",
            "Model_Type": "Regional Antarctic Viscoelastic (Post-LGM)",
            "Viscosity_Structure": "Upper mantle: 1.0e20 Pa s; reduced regional asthenosphere",
            "Lithospheric_Thickness_km": 65.0,
            "Northern_Peninsula_Uplift_mm_yr": "+2.0 to +4.5 mm/yr",
            "Southern_Palmer_Uplift_mm_yr": "+1.0 to +2.5 mm/yr",
            "Spatial_Gradient_Character": "Moderate regional gradient",
            "Time_Dependence": "Steady linear rate",
            "Peninsula_Geographical_Validity": "Moderate; partially captures thinner lithosphere but misses post-1995 rapid rebound",
            "Altimetric_Volume_Impact_km3_yr": "-0.4 to -0.9 km3/yr",
            "Gravimetric_Mass_Impact_Gt_yr": "+3 to +6 Gt/yr mass correction",
            "Methodological_Recommendation": "Intermediate sensitivity scenario"
        },
        {
            "Model_Name": "Nield et al. (2014) Regional Viscoelastic",
            "Reference": "Nield et al. (2014, EPSL / Nature 2014)",
            "Model_Type": "Regional 3D Low-Viscosity Viscoelastic + Decadal Transient",
            "Viscosity_Structure": "Low-viscosity slab window asthenosphere: 1.0e18 to 2.0e19 Pa s",
            "Lithospheric_Thickness_km": "30.0 to 50.0 km (very thin)",
            "Northern_Peninsula_Uplift_mm_yr": "+8.0 to +15.0 mm/yr (near Larsen B & Northern tip)",
            "Southern_Palmer_Uplift_mm_yr": "+1.5 to +3.5 mm/yr",
            "Spatial_Gradient_Character": "Extremely steep gradient; highly concentrated around collapsed shelf embayments",
            "Time_Dependence": "Strongly time-dependent! Maxwell relaxation time is ~3–15 years; uplift accelerated post-2002",
            "Peninsula_Geographical_Validity": "High; directly validated by UKANET / LARISSA continuous GPS stations",
            "Altimetric_Volume_Impact_km3_yr": "-1.5 to -3.2 km3/yr (crucial: avoids attributing solid Earth uplift to ice thickening)",
            "Gravimetric_Mass_Impact_Gt_yr": "+8 to +15 Gt/yr mass correction (prevents ~10 Gt/yr mass overestimation)",
            "Methodological_Recommendation": "Primary recommended regional GIA framework for northern Peninsula (Basin Ipp-J and northern I-Ipp)"
        },
        {
            "Model_Name": "Wolstencroft et al. (2015) GPS Empirical",
            "Reference": "Wolstencroft et al. (2015, Geophys. Res. Lett.)",
            "Model_Type": "Empirical GPS-Interpolated Vertical Crustal Motion",
            "Viscosity_Structure": "Empirically constrained by 19 continuous GPS stations (no explicit viscosity assumption)",
            "Lithospheric_Thickness_km": "Empirical",
            "Northern_Peninsula_Uplift_mm_yr": "+7.5 to +14.2 mm/yr",
            "Southern_Palmer_Uplift_mm_yr": "+1.8 to +3.0 mm/yr",
            "Spatial_Gradient_Character": "Empirical kriging interpolation; captures high spatial variability",
            "Time_Dependence": "Interpolated over 2002–2014 GPS observation era",
            "Peninsula_Geographical_Validity": "High at GPS station locations; unconstrained inland of the spine where GPS stations are absent",
            "Altimetric_Volume_Impact_km3_yr": "-1.4 to -2.9 km3/yr",
            "Gravimetric_Mass_Impact_Gt_yr": "+7 to +13 Gt/yr mass correction",
            "Methodological_Recommendation": "Direct empirical benchmark for validating regional viscoelastic models at station sites"
        },
        {
            "Model_Name": "Present-Day Elastic Rebound Model",
            "Reference": "Regional Green's Function convolution with contemporary ice loss",
            "Model_Type": "Pure Elastic Instantaneous Lithospheric Deformation",
            "Viscosity_Structure": "Instantaneous elastic half-space (shear modulus ~4.0e10 Pa)",
            "Lithospheric_Thickness_km": "Effective elastic thickness Te ~ 20 to 35 km",
            "Northern_Peninsula_Uplift_mm_yr": "+2.0 to +6.0 mm/yr (proportional to instantaneous ice loss)",
            "Southern_Palmer_Uplift_mm_yr": "+0.5 to +1.5 mm/yr",
            "Spatial_Gradient_Character": "Sharply localized within 20 km of dynamic glacier grounding lines",
            "Time_Dependence": "Strictly instantaneous; tracks contemporary annual ice mass loss rate D(t) - SMB(t)",
            "Peninsula_Geographical_Validity": "High; distinct physical mechanism that must NOT be confused with viscoelastic GIA",
            "Altimetric_Volume_Impact_km3_yr": "-0.4 to -1.1 km3/yr",
            "Gravimetric_Mass_Impact_Gt_yr": "+1 to +3 Gt/yr mass correction",
            "Methodological_Recommendation": "Mandatory separate additive correction: v_total = v_viscoelastic_GIA + v_elastic_instantaneous"
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "gia_model_comparison.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df

# -------------------------------------------------------------------------
# 5. Table: uncertainty_budget_design.csv
# -------------------------------------------------------------------------
def generate_uncertainty_budget_design():
    data = [
        # Measurement Uncertainties
        {
            "Source_Component": "Satellite Ice Velocity Tracking",
            "Discipline": "Ice Dynamics",
            "Uncertainty_Type": "Measurement Uncertainty (Random Observational Noise)",
            "Estimated_Magnitude": "+/- 5 to 20 m/yr (Sentinel-1); +/- 15 to 50 m/yr (Landsat-7)",
            "Units": "m/yr",
            "Correlation_Covariance_Structure": "Spatially correlated over ~5 km feature-tracking correlation length; temporally uncorrelated across independent sensor cycles",
            "Propagation_Method": "Standard error propagation across flux gates: sigma_D_obs = sqrt(sum((alpha * H * W_i * sigma_v_i)^2))",
            "Independent_or_Coupled": "Independent of SMB; coupled to flux gate width and orientation",
            "Impact_on_Cumulative_2024_Volume": "+/- 28 to 45 km3 ice-equivalent over 1979–2024"
        },
        {
            "Source_Component": "Satellite Laser & Radar Altimetry (dh/dt)",
            "Discipline": "Surface Elevation Change",
            "Uncertainty_Type": "Measurement Uncertainty (Sensor Noise & Footprint Slope Error)",
            "Estimated_Magnitude": "+/- 0.02 m/yr (ICESat-2 ATL15); +/- 0.08 m/yr (CryoSat-2); +/- 0.40 m/yr (ICESat-1 on slopes > 2°)",
            "Units": "m/yr",
            "Correlation_Covariance_Structure": "Strong spatial covariance along orbit tracks; severe slope-correlated bias in rugged alpine terrain",
            "Propagation_Method": "Kriging error covariance integration with slope quality flags (exclude slopes > 2° for ICESat-1)",
            "Independent_or_Coupled": "Coupled to topographic roughness and slope orientation",
            "Impact_on_Cumulative_2024_Volume": "+/- 35 to 60 km3 ice-equivalent (altimetric integration)"
        },
        {
            "Source_Component": "Ku-Band Radar Penetration Bias",
            "Discipline": "Radar Altimetry",
            "Uncertainty_Type": "Measurement / Geophysical Hazard",
            "Estimated_Magnitude": "+/- 0.5 to 2.5 m episodic penetration shift",
            "Units": "m apparent height",
            "Correlation_Covariance_Structure": "Correlated with summer surface melt events and wet snow facies",
            "Propagation_Method": "Mask out summer melt days using RACMO melt flags or apply dual-peak waveform retracking",
            "Independent_or_Coupled": "Coupled to surface melt and firn temperature",
            "Impact_on_Cumulative_2024_Volume": "+/- 20 to 35 km3 ice-equivalent"
        },

        # Model Uncertainties
        {
            "Source_Component": "RACMO2.4p1 Regional Atmospheric SMB",
            "Discipline": "Surface Mass Balance",
            "Uncertainty_Type": "Model Uncertainty (Atmospheric Physics & Downscaling)",
            "Estimated_Magnitude": "+/- 12% to 18% of annual regional SMB (~15 to 25 Gt/yr)",
            "Units": "Gt/yr (~16 to 27 km3/yr)",
            "Correlation_Covariance_Structure": "High spatial covariance within each basin; interannually uncorrelated; partial covariance across basins Hp-I and Ipp-J due to shared synoptic storm tracks",
            "Propagation_Method": "Ensemble spread and cross-validation against automatic weather station (AWS) accumulation records",
            "Independent_or_Coupled": "Coupled to firn densification model forcing (FDM uses RACMO SMB)",
            "Impact_on_Cumulative_2024_Volume": "+/- 85 to 130 km3 ice-equivalent over 45 years"
        },
        {
            "Source_Component": "Firn Air Content Evolution (dFAC/dt)",
            "Discipline": "Firn Densification",
            "Uncertainty_Type": "Model Uncertainty (1D Firn Compaction Physics)",
            "Estimated_Magnitude": "+/- 0.15 to 0.40 m/yr FAC change rate",
            "Units": "m firn air / yr",
            "Correlation_Covariance_Structure": "Spatially correlated across elevation bands; high covariance with summer melt and winter snowfall anomalies",
            "Propagation_Method": "IMAU-FDM model parameter perturbation and density profile validation against shallow firn cores",
            "Independent_or_Coupled": "Directly coupled to RACMO melt and accumulation forcing",
            "Impact_on_Cumulative_2024_Volume": "+/- 25 to 45 km3 ice-equivalent"
        },
        {
            "Source_Component": "Regional Slab-Window GIA Uplift",
            "Discipline": "Solid Earth Geophysics",
            "Uncertainty_Type": "Model Uncertainty (Mantle Viscosity & Ice History)",
            "Estimated_Magnitude": "+/- 3.0 to 6.0 mm/yr in Northern Peninsula; +/- 1.0 mm/yr in Palmer Land",
            "Units": "mm/yr uplift",
            "Correlation_Covariance_Structure": "Long spatial correlation length (~100 km) centered on slab window; multi-decadal time dependence",
            "Propagation_Method": "Ensemble sensitivity testing across Nield (2014) viscosity scenarios vs W12a continental baseline",
            "Independent_or_Coupled": "Coupled to post-1995 dynamic ice loss via time-dependent viscoelastic response",
            "Impact_on_Cumulative_2024_Volume": "+/- 40 to 80 km3 ice-equivalent over 1979–2024"
        },

        # Scenario Uncertainties
        {
            "Source_Component": "Unobserved Historical Discharge (1979–1999)",
            "Discipline": "Ice Dynamics",
            "Uncertainty_Type": "Scenario Uncertainty (Alternative Parameterizations)",
            "Estimated_Magnitude": "Low: Steady-state (D = SMB_mean); Central: InSAR-scaled IOM; High: Pre-collapse dynamic opening (+15%)",
            "Units": "Gt/yr & km3/yr",
            "Correlation_Covariance_Structure": "Decadal step-function / trend uncertainty; strongly affects early cumulative volume trajectory",
            "Propagation_Method": "Three explicit scenario trajectories (Low, Central, High) tracked through all downstream calculations; explicitly reported as scenario spread, NOT averaged",
            "Independent_or_Coupled": "Independent of contemporary 2014–2024 observations; constrained only by regional IMBIE benchmark",
            "Impact_on_Cumulative_2024_Volume": "+/- 65 to 110 km3 ice-equivalent divergence by 1999"
        },

        # Structural Uncertainties
        {
            "Source_Component": "Bedmap3 vs BedMachine Common-Domain Thickness",
            "Discipline": "Bed Topography & Ice Thickness",
            "Uncertainty_Type": "Structural Uncertainty (Inter-Product Structural Divergence)",
            "Estimated_Magnitude": "+7,204.9 km3 (+5.40% on identical 216,062.2 km2 Domain A footprint)",
            "Units": "km3 ice-equivalent",
            "Correlation_Covariance_Structure": "Systematic positive offset (BedMachine is thicker across 89.2% of common domain); NOT random white noise; spatially concentrated in deep glacier troughs",
            "Propagation_Method": "MUST NOT BE CONVERTED TO A GAUSSIAN CONFIDENCE INTERVAL. Maintained as two separate baseline realizations; discharge gates integrated under BOTH geometries to evaluate flux sensitivity.",
            "Independent_or_Coupled": "Coupled to flux gate depth integration (affects D through H_mean: Gate discharge differs by ~4–6% between products)",
            "Impact_on_Cumulative_2024_Volume": "Initial baseline offset: +7,204.9 km3; Cumulative 1979–2024 trajectory divergence: ~18 to 32 km3"
        },
        {
            "Source_Component": "Bedmap3 Candidate Rock / Nunatak Volume",
            "Discipline": "Mask Classification & Nunatak Interpolation",
            "Uncertainty_Type": "Structural Uncertainty (Mask Boundary Disagreement)",
            "Estimated_Magnitude": "+620.3 km3 ice-equivalent across 18,628 cells (4,608.5 km2)",
            "Units": "km3 ice-equivalent",
            "Correlation_Covariance_Structure": "Concentrated exclusively on steep high-elevation mountain ridges and nunatak borders",
            "Propagation_Method": "Evaluated under three discrete hypothesis scenarios (H1: 0 km3 bare rock; H2: Static ice mantle with SMB-only thinning; H3: Static offset). Never dynamically thinned.",
            "Independent_or_Coupled": "Decoupled from primary Domain A dynamic flux gates",
            "Impact_on_Cumulative_2024_Volume": "Discrete structural shift of 0.0 to 620.3 km3 (baseline offset; zero dynamic trajectory contamination)"
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "uncertainty_budget_design.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df

# -------------------------------------------------------------------------
# 6. Figures: 3 Publication-Quality Architecture & Workflow Diagrams
# -------------------------------------------------------------------------
def generate_diagram_data_flow():
    """Generates diagram_phase3_1b_data_flow_architecture.png"""
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7.5, 9.6, "Phase 3.1B: Historical Ice-Volume Reconstruction Architecture", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#1a2a3a')
    ax.text(7.5, 9.25, "Three-Epoch Hybrid Evidence Framework & Primary Trajectory Domain A", 
            ha='center', va='center', fontsize=12, style='italic', color='#4a5568')

    # Epoch 1 Box
    p1 = FancyBboxPatch((0.5, 5.2), 4.2, 3.6, boxstyle="round,pad=0.2", ec="#c53030", fc="#fff5f5", lw=2)
    ax.add_patch(p1)
    ax.text(2.6, 8.5, "Epoch 1: 1979–1999\n[Model-Assisted]", ha='center', va='center', fontsize=12, fontweight='bold', color='#9b2c2c')
    ax.text(2.6, 7.3, "• SMB: RACMO2.3p2 / 2.4p1 (ERA)\n  [Provenance: Model Output]\n• Velocity: Pre-collapse Baseline\n  (1996 ERS InSAR snapshot)\n  [Provenance: Parameterized/Assumed]\n• Discharge Scenarios:\n  - Low: Balance flux (D = SMB)\n  - Central: InSAR-scaled IOM\n  - High: Accelerated late-90s\n• Altimetry/Gravimetry: None", 
            ha='left', va='center', fontsize=9.5, color='#2d3748')

    # Epoch 2 Box
    p2 = FancyBboxPatch((5.4, 5.2), 4.2, 3.6, boxstyle="round,pad=0.2", ec="#d69e2e", fc="#fffff0", lw=2)
    ax.add_patch(p2)
    ax.text(7.5, 8.5, "Epoch 2: 2000–2013\n[Multi-Sensor Constrained]", ha='center', va='center', fontsize=12, fontweight='bold', color='#b7791f')
    ax.text(7.5, 7.3, "• SMB: RACMO2.3p2 / 2.4p1\n  [Provenance: Model Output]\n• Velocity: Landsat-7 / Envisat\n  [Provenance: Gap-Filled / Interpolated]\n• Post-Collapse Surges:\n  Larsen B Crane/Green/Hektoria\n• Altimetry: ICESat-1 (campaigns)\n  [Provenance: Direct Obs (slopes<2°)]\n• Gravimetry: GRACE mascons (~300km)\n  [Provenance: Regional Constraint]", 
            ha='left', va='center', fontsize=9.5, color='#2d3748')

    # Epoch 3 Box
    p3 = FancyBboxPatch((10.3, 5.2), 4.2, 3.6, boxstyle="round,pad=0.2", ec="#2b6cb0", fc="#ebf8ff", lw=2)
    ax.add_patch(p3)
    ax.text(12.4, 8.5, "Epoch 3: 2014–2024\n[Observation-Rich Period]", ha='center', va='center', fontsize=12, fontweight='bold', color='#2b6cb0')
    ax.text(12.4, 7.3, "• SMB: RACMO2.4p1 (ERA5)\n  [Provenance: Model Output]\n• Velocity: Sentinel-1 & Landsat-8/9\n  [Provenance: Direct Observation]\n• Flux Gates: Annual gate discharge\n  across 8 verified systems\n• Altimetry: CryoSat-2 SARIn &\n  ICESat-2 ATL15 laser grids\n• Gravimetry: GRACE-FO mascons\n  Remaining: Penetration & GIA", 
            ha='left', va='center', fontsize=9.5, color='#2d3748')

    # Arrows down to Integration Engine
    for x in [2.6, 7.5, 12.4]:
        ax.annotate('', xy=(7.5, 4.4), xytext=(x, 5.1),
                    arrowprops=dict(arrowstyle="->", color="#4a5568", lw=2, mutation_scale=15))

    # Central Integration Engine
    p_engine = FancyBboxPatch((2.5, 2.7), 10.0, 1.6, boxstyle="round,pad=0.2", ec="#2f855a", fc="#f0fff4", lw=2.5)
    ax.add_patch(p_engine)
    ax.text(7.5, 4.0, "Input-Output & Mass Continuity Integration Engine (Domain A: 216,062.2 km²)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#22543d')
    ax.text(7.5, 3.3, "dV_ice_eq/dt = [ SMB_A(t) - D_A(t) ] / 0.917   [km³/yr]\nReconciled against Regional IMBIE-3 Benchmark (APIS Sector Reconciled Total: 1979–2023)\nGeophysical Corrections Applied: Low-Viscosity Slab-Window GIA + Elastic Rebound + FAC Compaction", 
            ha='center', va='center', fontsize=9.5, color='#1c4532')

    # Arrows to Dual Baselines
    ax.annotate('', xy=(4.0, 1.8), xytext=(5.5, 2.6),
                arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=2, mutation_scale=15))
    ax.annotate('', xy=(11.0, 1.8), xytext=(9.5, 2.6),
                arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=2, mutation_scale=15))

    # Dual Baseline Outputs
    p_bm3 = FancyBboxPatch((1.0, 0.4), 6.0, 1.3, boxstyle="round,pad=0.2", ec="#805ad5", fc="#faf5ff", lw=2)
    ax.add_patch(p_bm3)
    ax.text(4.0, 1.3, "Baseline Realization 1: Bedmap3 Domain A", ha='center', va='center', fontsize=11, fontweight='bold', color='#553c9e')
    ax.text(4.0, 0.8, "V_common(t) = 133,497.6 km³ + ΔV_ice_eq(t)\n[Domain B Nunataks (620.3 km³) Tracked Separately as Static]", 
            ha='center', va='center', fontsize=8.5, color='#44337a')

    p_bm4 = FancyBboxPatch((8.0, 0.4), 6.0, 1.3, boxstyle="round,pad=0.2", ec="#319795", fc="#e6fffa", lw=2)
    ax.add_patch(p_bm4)
    ax.text(11.0, 1.3, "Baseline Realization 2: BedMachine V4.1 Domain A", ha='center', va='center', fontsize=11, fontweight='bold', color='#234e52')
    ax.text(11.0, 0.8, "V_common(t) = 140,702.5 km³ + ΔV_ice_eq(t)\n[Strict Common Domain Footprint: 216,062.2 km²]", 
            ha='center', va='center', fontsize=8.5, color='#234e52')

    # Middle Structural Offset Label
    ax.text(7.5, 1.0, "Structural Offset\nΔ = +7,204.9 km³ (+5.40%)\n[Preserved, Not Averaged]", 
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#c53030',
            bbox=dict(boxstyle="square,pad=0.3", fc="#fff5f5", ec="#feb2b2"))

    out_fig = os.path.join(FIGURES_DIR, "diagram_phase3_1b_data_flow_architecture.png")
    plt.tight_layout()
    plt.savefig(out_fig, dpi=300)
    plt.close()
    print(f"Saved: {out_fig}")

def generate_diagram_correction_sequence():
    """Generates diagram_phase3_1b_correction_sequence.png"""
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(7.0, 9.6, "Geophysical Correction Sequence & Separation of Vertical Motions", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1a2a3a')
    ax.text(7.0, 9.25, "Physical Disentanglement of Bedrock Uplift, Firn Compaction, and Sensor Artifacts", 
            ha='center', va='center', fontsize=11, style='italic', color='#4a5568')

    steps = [
        ("Step 1: Raw Observation", 
         "Satellite Altimetry: dh_raw/dt (m/yr)\nSatellite Gravimetry: dM_raw/dt (Gt/yr)", 
         "#4a5568", "#edf2f7", 8.0),
        ("Step 2: Altimetry Sensor Corrections", 
         "• Radar Waveform Retracking (CryoSat-2 SARIn)\n• Slope Migration & Roughness Masking (slopes < 2° for ICESat-1)\n• Ku-Band Melt Season Penetration Masking (0.5–4.5 m shift)", 
         "#c53030", "#fff5f5", 6.3),
        ("Step 3: Firn Air Content Compaction Correction", 
         "• IMAU-FDM 1D Firn Model: Subtract dFAC/dt (m/yr)\n• Isolates True Solid-Ice Height Change: dh_ice/dt = dh_surf/dt - dFAC/dt\n• Critical: FDM forced by RACMO2.3p2 tipping-bucket percolation", 
         "#d69e2e", "#fffff0", 4.6),
        ("Step 4: Separation of Solid Earth Vertical Motions", 
         "v_total_vertical = v_viscoelastic_GIA + v_elastic_instantaneous\n• Viscoelastic GIA: Regional slab-window model (Nield 2014; +8 to +15 mm/yr in N-AP; +2 mm/yr south)\n• Elastic Uplift: Instantaneous Green's function convolution with unloading (+2 to +6 mm/yr near outlets)", 
         "#805ad5", "#faf5ff", 2.9),
        ("Step 5: Dynamic Reconciled Output", 
         "True Grounded Solid Ice-Equivalent Rate:\n(dV_ice_eq/dt)_alt = sum[ (dh_ice/dt - v_total_vertical) * A_i ]\nDirectly Comparable to Input-Output Method: (dV_ice_eq/dt)_IOM = (SMB - D) / 0.917", 
         "#2f855a", "#f0fff4", 1.2)
    ]

    for i, (title, desc, ec_col, fc_col, y_pos) in enumerate(steps):
        p = FancyBboxPatch((1.5, y_pos - 0.6), 11.0, 1.2, boxstyle="round,pad=0.2", ec=ec_col, fc=fc_col, lw=2)
        ax.add_patch(p)
        ax.text(2.0, y_pos + 0.3, title, fontsize=11, fontweight='bold', color=ec_col)
        ax.text(2.0, y_pos - 0.2, desc, fontsize=9.0, color='#2d3748')
        if i < len(steps) - 1:
            ax.annotate('', xy=(7.0, y_pos - 0.65), xytext=(7.0, y_pos - 0.85),
                        arrowprops=dict(arrowstyle="<-", color="#718096", lw=2.5, mutation_scale=15))

    out_fig = os.path.join(FIGURES_DIR, "diagram_phase3_1b_correction_sequence.png")
    plt.tight_layout()
    plt.savefig(out_fig, dpi=300)
    plt.close()
    print(f"Saved: {out_fig}")

def generate_diagram_uncertainty_propagation():
    """Generates diagram_phase3_1b_uncertainty_propagation.png"""
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(7.5, 9.6, "Phase 3.1B: Uncertainty Budget & Error Propagation Architecture", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1a2a3a')
    ax.text(7.5, 9.25, "Rigorous Partitioning of Measurement, Model, Scenario, and Structural Uncertainties", 
            ha='center', va='center', fontsize=11, style='italic', color='#4a5568')

    # Four Uncertainty Category Boxes
    cats = [
        ("Measurement Uncertainty\n[Random Observational Noise]", 
         "• Sentinel-1 / Landsat-8 velocity noise: +/- 5–20 m/yr\n• ICESat-2 ATL15 altimetry noise: +/- 0.02 m/yr\n• GRACE mascon instrument noise\n• Flux gate coordinate registration\n--> Propagated via Quadrature Covariance:\n    sigma_meas = sqrt(sigma_v^2 + sigma_h^2)", 
         "#2b6cb0", "#ebf8ff", 0.5, 5.0, 3.2, 3.8),
        ("Model Uncertainty\n[Physical Approximations]", 
         "• RACMO2.4p1 SMB physics: +/- 15%\n  (~15–25 Gt/yr regional spread)\n• IMAU-FDM firn compaction: +/- 15%\n• Slab-window GIA mantle viscosity:\n  eta = 1e18 vs 1e19 Pa s (+/- 3–6 mm/yr)\n• Depth-averaged velocity ratio alpha (0.80–0.95)\n--> Propagated via Model Ensembles", 
         "#d69e2e", "#fffff0", 4.1, 5.0, 3.2, 3.8),
        ("Scenario Uncertainty\n[Unobserved Pre-2000 Period]", 
         "• 1979–1999 Unobserved Discharge:\n  - Low: Steady balance (D = SMB)\n  - Central: InSAR-scaled IOM\n  - High: Pre-collapse opening (+15%)\n• Divergence: +/- 65 to 110 km³ by 1999\n--> Explicitly Reported as 3 Divergent\n    Scenario Trajectories (NOT Averaged!)", 
         "#c53030", "#fff5f5", 7.7, 5.0, 3.2, 3.8),
        ("Structural Uncertainty\n[Discrete Model Realizations]", 
         "• Bedmap3 vs BedMachine Thickness:\n  +7,204.9 km³ (+5.40% on Domain A)\n  [BedMachine thicker across 89.2%]\n• Bedmap3 Nunatak Cells (4,608.5 km²):\n  620.3 km³ (Bare rock vs Ice mantle)\n--> DO NOT CONVERT TO GAUSSIAN SIGMA!\n    Maintained as Dual Baseline Trajectories", 
         "#805ad5", "#faf5ff", 11.3, 5.0, 3.2, 3.8)
    ]

    for title, desc, ec_col, fc_col, x, y, w, h in cats:
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", ec=ec_col, fc=fc_col, lw=2)
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 0.5, title, ha='center', va='center', fontsize=10.5, fontweight='bold', color=ec_col)
        ax.text(x + 0.15, y + h/2 - 0.5, desc, ha='left', va='center', fontsize=8.5, color='#2d3748')
        ax.annotate('', xy=(7.5, 3.4), xytext=(x + w/2, y - 0.1),
                    arrowprops=dict(arrowstyle="->", color="#4a5568", lw=1.8, mutation_scale=12))

    # Consolidated Output Box
    p_out = FancyBboxPatch((1.5, 0.6), 12.0, 2.5, boxstyle="round,pad=0.2", ec="#2f855a", fc="#f0fff4", lw=2.5)
    ax.add_patch(p_out)
    ax.text(7.5, 2.7, "Final Historical Volume Trajectory Uncertainty Representation", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#22543d')
    ax.text(7.5, 1.6, "1. Dual Baseline Realizations: Trajectories anchored independently to Bedmap3 (133,497.6 km³) and BedMachine (140,702.5 km³)\n2. Three Discharge Scenario Branches: Low, Central, and High curves displayed across 1979–1999 to show unmeasured dynamic spread\n3. Statistical Confidence Envelope: 1-sigma and 2-sigma shaded bands around Central curve combining measurement & model quadrature\n4. Regional Benchmark Overlay: Otosaka et al. (2026) IMBIE reconciled series plotted as independent regional sector envelope\n5. Structural Isolation: +7,204.9 km³ baseline gap and 620.3 km³ nunatak uncertainty explicitly kept outside Gaussian error bands", 
            ha='center', va='center', fontsize=9.0, color='#1c4532')

    out_fig = os.path.join(FIGURES_DIR, "diagram_phase3_1b_uncertainty_propagation.png")
    plt.tight_layout()
    plt.savefig(out_fig, dpi=300)
    plt.close()
    print(f"Saved: {out_fig}")

# -------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("PHASE 3.1B: HISTORICAL RECONSTRUCTION METHODOLOGY DESIGN")
    print("=" * 80)
    generate_epoch_methodology_matrix()
    generate_reconstruction_provenance_matrix()
    generate_domain_implementation_matrix()
    generate_gia_model_comparison()
    generate_uncertainty_budget_design()
    print("Generating Figure 1: Data Flow Architecture Diagram...")
    generate_diagram_data_flow()
    print("Generating Figure 2: Correction Sequence Diagram...")
    generate_diagram_correction_sequence()
    print("Generating Figure 3: Uncertainty Propagation Tree...")
    generate_diagram_uncertainty_propagation()
    print("\nPhase 3.1B Tables and Diagrams Successfully Created.")

if __name__ == "__main__":
    main()

