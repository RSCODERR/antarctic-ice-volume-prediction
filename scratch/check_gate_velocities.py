import os, sys
import pandas as pd

df_prof = pd.read_csv('reports/tables/phase5_stage3C_velocity_profiles.csv')

# Let's inspect Millett (FL_HPI_02)
millet = df_prof[df_prof['Glacier_ID'] == 'FL_HPI_02']
gl_millet = millet[millet['Cell_Index'] == 84].iloc[0]
print(f"Millett GL Cell 84 (x = {gl_millet['Distance_From_Divide_km']} km): u = {gl_millet['Simulated_Velocity_m_yr']} m/yr")

# Gate is 8.0 km upstream of GL: 42.25 - 8.0 = 34.25 km -> Cell index ~ 68
gate_millet = millet[abs(millet['Distance_From_Divide_km'] - 34.25) < 0.6]
for idx, r in gate_millet.iterrows():
    print(f"Millett ~8 km Upstream Cell {r['Cell_Index']} (x = {r['Distance_From_Divide_km']} km): u = {r['Simulated_Velocity_m_yr']:.2f} m/yr, H = {r['Ice_Thickness_m']:.1f} m, Bed = {r['Bed_Elevation_m']:.1f} m, Surf = {r['Surface_Elevation_m']:.1f} m")

# Flask (FL_IPPJ_03)
flask = df_prof[df_prof['Glacier_ID'] == 'FL_IPPJ_03']
gl_flask = flask[flask['Cell_Index'] == 58].iloc[0]
print(f"\nFlask GL Cell 58 (x = {gl_flask['Distance_From_Divide_km']} km): u = {gl_flask['Simulated_Velocity_m_yr']} m/yr")

# Gate is 7.0 km upstream of GL: 29.25 - 7.0 = 22.25 km -> Cell index ~ 44
gate_flask = flask[abs(flask['Distance_From_Divide_km'] - 22.25) < 0.6]
for idx, r in gate_flask.iterrows():
    print(f"Flask ~7 km Upstream Cell {r['Cell_Index']} (x = {r['Distance_From_Divide_km']} km): u = {r['Simulated_Velocity_m_yr']:.2f} m/yr, H = {r['Ice_Thickness_m']:.1f} m, Bed = {r['Bed_Elevation_m']:.1f} m, Surf = {r['Surface_Elevation_m']:.1f} m")

# Drygalski (FL_IPPJ_01)
drygalski = df_prof[df_prof['Glacier_ID'] == 'FL_IPPJ_01']
gl_dry = drygalski[drygalski['Cell_Index'] == 71].iloc[0]
print(f"\nDrygalski GL Cell 71 (x = {gl_dry['Distance_From_Divide_km']} km): u = {gl_dry['Simulated_Velocity_m_yr']} m/yr")
# Drygalski upstream cells
for d in [5.0, 7.5, 10.0]:
    up = drygalski[abs(drygalski['Distance_From_Divide_km'] - (35.75 - d)) < 0.6]
    if len(up) > 0:
        r = up.iloc[0]
        print(f"Drygalski ~{d} km Upstream Cell {r['Cell_Index']} (x = {r['Distance_From_Divide_km']} km): u = {r['Simulated_Velocity_m_yr']:.2f} m/yr, H = {r['Ice_Thickness_m']:.1f} m, Bed = {r['Bed_Elevation_m']:.1f} m, Surf = {r['Surface_Elevation_m']:.1f} m")

