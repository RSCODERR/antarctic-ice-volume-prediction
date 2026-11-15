import os, sys
import pandas as pd
import numpy as np

df_prof = pd.read_csv('reports/tables/phase5_stage3C_velocity_profiles.csv')

for fl_id in ['FL_HPI_02', 'FL_IPPJ_03', 'FL_IPPJ_01']:
    sub = df_prof[df_prof['Glacier_ID'] == fl_id].copy()
    sub['slope'] = -np.gradient(sub['Surface_Elevation_m'], sub['Distance_From_Divide_km'] * 1000.0)
    gl_row = sub[sub['Cell_Index'] == (84 if fl_id=='FL_HPI_02' else (58 if fl_id=='FL_IPPJ_03' else 71))].iloc[0]
    
    print(f"\n==================== {fl_id} ====================")
    print(f"Profile length: {len(sub)} cells ({sub['Distance_From_Divide_km'].max():.2f} km)")
    print(f"Grounded cells: {sum(sub['Grounding_Line_Status']=='Grounded')}, Floating cells: {sum(sub['Grounding_Line_Status']!='Grounded')}")
    print(f"GL Cell Index: {gl_row['Cell_Index']}, GL Distance: {gl_row['Distance_From_Divide_km']:.2f} km")
    print(f"At GL: Bed = {gl_row['Bed_Elevation_m']:.2f} m, Surf = {gl_row['Surface_Elevation_m']:.2f} m, H = {gl_row['Ice_Thickness_m']:.2f} m, Slope = {gl_row['slope']:.4e}, u = {gl_row['Simulated_Velocity_m_yr']:.2f} m/yr")
    
    # Flotation check at GL:
    # Ice is afloat if -bed * rho_w / rho_i >= H, or flotation thickness H_f = -bed * rho_w / rho_i (if bed < 0)
    rho_w = 1028.0
    rho_i = 917.0
    if gl_row['Bed_Elevation_m'] < 0:
        H_float = -gl_row['Bed_Elevation_m'] * (rho_w / rho_i)
        flot_ratio = gl_row['Ice_Thickness_m'] / H_float
        print(f"Flotation thickness at GL: {H_float:.2f} m, Actual H: {gl_row['Ice_Thickness_m']:.2f} m, Ratio H/H_f: {flot_ratio:.3f}")
    
    # Profile averages:
    print(f"Mean Grounded H: {sub[sub['Grounding_Line_Status']=='Grounded']['Ice_Thickness_m'].mean():.2f} m")
    print(f"Mean Grounded Bed: {sub[sub['Grounding_Line_Status']=='Grounded']['Bed_Elevation_m'].mean():.2f} m")
    print(f"Mean Grounded Slope: {sub[sub['Grounding_Line_Status']=='Grounded']['slope'].mean():.4e}")

