import os, sys
if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')
sys.path.insert(0, '.')
sys.path.insert(0, 'src')

import numpy as np
import netCDF4 as nc
import pandas as pd
from physics.constants import CONST

df_prof = pd.read_csv('reports/tables/phase5_stage3C_velocity_profiles.csv')

for fl_id in df_prof['Glacier_ID'].unique():
    sub = df_prof[df_prof['Glacier_ID'] == fl_id]
    gl_row = sub[sub['Grounding_Line_Status'].str.contains('Grounding', case=False, na=False)]
    print(f"\n=======================================================")
    print(f"Flowline: {fl_id}")
    print(f"Total cells: {len(sub)}")
    print(f"Grounding line statuses: {sub['Grounding_Line_Status'].value_counts().to_dict()}")
    if len(gl_row) > 0:
        row = gl_row.iloc[0]
        print(f"GL Row: Cell {row['Cell_Index']}, Dist {row['Distance_From_Divide_km']} km, u = {row['Simulated_Velocity_m_yr']} m/yr, H = {row['Ice_Thickness_m']} m, Bed = {row['Bed_Elevation_m']} m, Surf = {row['Surface_Elevation_m']} m")
        gl_dist = row['Distance_From_Divide_km']
        # Look 7-8 km upstream of GL
        up_dist = gl_dist - 7.5
        up_cells = sub[abs(sub['Distance_From_Divide_km'] - up_dist) < 0.6]
        if len(up_cells) > 0:
            print(f"~7.5 km Upstream of GL: Cell {up_cells.iloc[0]['Cell_Index']}, Dist {up_cells.iloc[0]['Distance_From_Divide_km']} km, u = {up_cells.iloc[0]['Simulated_Velocity_m_yr']} m/yr")
    else:
        # Check last grounded cell
        grounded = sub[sub['Grounding_Line_Status'] == 'Grounded']
        if len(grounded) > 0:
            last_g = grounded.iloc[-1]
            print(f"Last Grounded Cell: Cell {last_g['Cell_Index']}, Dist {last_g['Distance_From_Divide_km']} km, u = {last_g['Simulated_Velocity_m_yr']} m/yr")

print("\n--- Gate Inventory Check ---")
df_gates = pd.read_csv('reports/tables/flux_gate_inventory.csv')
for idx, r in df_gates.iterrows():
    print(f"{r['Gate_ID']}: {r['Glacier_System']} | Dist_GL: {r['Distance_Upstream_GL_km']} km | Width: {r['Gate_Width_km']} km | Mean_v: {r['Mean_v_perp_m_yr']} m/yr | Ref: {r['Grounding_Line_Ref']} | Years: {r['Direct_Obs_Years']}")
