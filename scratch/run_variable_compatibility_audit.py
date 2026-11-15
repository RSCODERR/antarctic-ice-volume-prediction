import os
import pandas as pd

BASE_DIR = os.path.abspath('antarctic-ice-volume-prediction')
TABLES_DIR = os.path.join(BASE_DIR, 'reports', 'tables')
os.makedirs(TABLES_DIR, exist_ok=True)

variables = [
    {
        'Variable_Identifier': 'ivaf',
        'Long_Name': 'Ice volume above floatation',
        'Physical_Units': 'm^3 of ice (convertible to km^3 by 1e-9)',
        'Physical_Definition': 'Integrated volume of ice column exceeding hydrostatic flotation threshold: integral(H - H_f) dA, where H_f = -rho_w/rho_i * z_bed for marine-grounded ice (z_bed < 0), and H_f = 0 for land-grounded ice.',
        'Supports_Primary_Target': 'CONDITIONAL / INCOMPATIBLE AS DIRECT ADDITION',
        'Glaciological_Role_and_Limitation': 'Direct physical proxy for sea-level rise potential (GMSL). Omits submerged ice column below sea level (H_sub = min(H, H_f)) that already displaces seawater. As grounding line retreats, Delta_VAF != Delta_V_grounded because the submerged portion is excluded from VAF.',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'Must remain strictly separate from grounded ice-equivalent volume baseline. Can only be added to baseline if full bedrock bathymetry and flotation thickness fields H_f(x,y) are integrated synchronously.',
        'Availability_in_Archive': 'Available across all 16 models and 26 experiments in ComputedScalarsPaper.zip.'
    },
    {
        'Variable_Identifier': 'icevol (ivol)',
        'Long_Name': 'Total ice volume (grounded + floating)',
        'Physical_Units': 'm^3 of ice (convertible to km^3 by 1e-9)',
        'Physical_Definition': 'Total geometric volume of all ice within the sector/region: V_total = V_grounded + V_floating_shelf.',
        'Supports_Primary_Target': 'INCOMPATIBLE',
        'Glaciological_Role_and_Limitation': 'Conflates grounded ice with floating ice shelves. Floating ice shelf volume changes displace seawater and do not reflect grounded solid ice volume changes. Cannot support grounded target without explicit shelf mask separation.',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'Requires subtracting floating ice shelf volume: V_grounded = V_total - V_shelf.',
        'Availability_in_Archive': 'Available across all 16 models in ComputedScalarsPaper.zip.'
    },
    {
        'Variable_Identifier': 'vaf / icevolg',
        'Long_Name': 'Volume of grounded ice',
        'Physical_Units': 'm^3 of ice (convertible to km^3 by 1e-9)',
        'Physical_Definition': 'Total geometric volume of ice resting on subglacial bedrock: integral_grounded H dA.',
        'Supports_Primary_Target': 'COMPATIBLE WITH FIRN ADJUSTMENT',
        'Glaciological_Role_and_Limitation': 'Represents total grounded geometric volume. Includes submerged marine ice. To convert to solid ice equivalent, must account for firn air content (FAC).',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'Requires solid ice density adjustment (V_ice_eq = V_grounded - V_FAC) and baseline calibration.',
        'Availability_in_Archive': 'Not universally archived as standalone scalar in ComputedScalarsPaper.zip; only stored in subsets or 2D grids.'
    },
    {
        'Variable_Identifier': 'iareagr',
        'Long_Name': 'Grounded ice area',
        'Physical_Units': 'm^2 (convertible to km^2 by 1e-6)',
        'Physical_Definition': 'Planimetric surface area of bedrock covered by grounded ice sheet.',
        'Supports_Primary_Target': 'AUXILIARY STATE ONLY',
        'Glaciological_Role_and_Limitation': 'State variable tracking grounding-line retreat/advance. Dimensionally area (L^2), not volume (L^3). Cannot be added to volume baseline.',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'N/A (Spatial area metric only).',
        'Availability_in_Archive': 'Available across all 16 models in ComputedScalarsPaper.zip.'
    },
    {
        'Variable_Identifier': 'iareafl',
        'Long_Name': 'Floating ice shelf area',
        'Physical_Units': 'm^2 (convertible to km^2 by 1e-6)',
        'Physical_Definition': 'Planimetric surface area of floating ice shelves extending seaward of the grounding line.',
        'Supports_Primary_Target': 'AUXILIARY STATE ONLY',
        'Glaciological_Role_and_Limitation': 'Key dynamic buttressing descriptor. Tracks catastrophic ice-shelf collapse (e.g. Larsen A/B/C). Dimensionally area (L^2).',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'N/A (Buttressing proxy only).',
        'Availability_in_Archive': 'Available across all 16 models in ComputedScalarsPaper.zip.'
    },
    {
        'Variable_Identifier': 'smbgr',
        'Long_Name': 'Surface mass balance on grounded ice',
        'Physical_Units': 'kg/m^2/s or Gt/yr',
        'Physical_Definition': 'Integrated mass accumulation (snowfall) minus mass ablation (sublimation, runoff) over grounded ice.',
        'Supports_Primary_Target': 'FLUX COMPONENT ONLY',
        'Glaciological_Role_and_Limitation': 'Primary atmospheric driving flux. Related to volume change via dM/dt = SMB - Discharge. Does not directly equal net volume change without dynamic discharge.',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'Requires time integration and ice discharge subtraction: Delta_M = integral (SMB - D) dt.',
        'Availability_in_Archive': 'Not in ComputedScalarsPaper.zip; archived in 2D spatial NetCDF fields on GHub.'
    },
    {
        'Variable_Identifier': 'discharge / calving',
        'Long_Name': 'Ice discharge across grounding line / Calving flux',
        'Physical_Units': 'kg/m^2/s or Gt/yr',
        'Physical_Definition': 'Dynamic ice flux crossing the grounding line (D = integral rho_i * H * u_gl * n dl) or calving front flux.',
        'Supports_Primary_Target': 'FLUX COMPONENT ONLY',
        'Glaciological_Role_and_Limitation': 'Primary dynamic loss flux. Coupled with SMB in mass balance conservation. Cannot be used in isolation.',
        'Direct_Addition_to_Baseline_Permitted': False,
        'Conversion_Requirement': 'Requires mass conservation coupling: dV/dt = (SMB - D) / rho_ice.',
        'Availability_in_Archive': 'Not in ComputedScalarsPaper.zip; archived in 2D spatial NetCDF fields on GHub.'
    }
]

df_var = pd.DataFrame(variables)
out_csv = os.path.join(TABLES_DIR, 'ismip6_target_variable_compatibility.csv')
df_var.to_csv(out_csv, index=False)
print(f"Saved {out_csv} ({len(df_var)} rows)")

