import os
import pandas as pd

BASE_DIR = os.path.abspath('antarctic-ice-volume-prediction')
TABLES_DIR = os.path.join(BASE_DIR, 'reports', 'tables')
os.makedirs(TABLES_DIR, exist_ok=True)

scenarios_audit = [
    {
        'Scenario_Designation': 'CMIP5 RCP8.5',
        'Emissions_Pathway_Class': 'High Emissions / High Warming (Radiative forcing ~8.5 W/m2 by 2100)',
        'Driving_Climate_Models': 'NorESM1-M, MIROC-ESM-CHEM, CCSM4, HadGEM2-ES, CSIRO-Mk3.6.0, IPSL-CM5A-MR',
        'Atmospheric_Forcing_Availability': 'Fully Available (RACMO2.3p2 / MAR downscaled anomalies)',
        'Oceanic_Thermal_Forcing_Availability': 'Fully Available (Standard, PIGL, MeanAnt, Open calibrations)',
        'Ice_Sheet_Model_Simulations_Count': 16,
        'Simulation_Status_in_ISMIP6': 'OFFICIAL CORE TIER-1 EXPERIMENT (exp05, exp06, exp08-13)',
        'Linear_Interpolation_Permitted': 'N/A (Authentic multi-model ensemble exists)',
        'Operational_Status_for_Phase5': 'APPROVED AS PRIMARY HIGH-EMISSIONS BENCHMARK'
    },
    {
        'Scenario_Designation': 'CMIP5 RCP2.6',
        'Emissions_Pathway_Class': 'Strong Mitigation / Paris Agreement (Radiative forcing ~2.6 W/m2 by 2100)',
        'Driving_Climate_Models': 'NorESM1-M, IPSL-CM5A-MR',
        'Atmospheric_Forcing_Availability': 'Fully Available (RACMO2.3p2 downscaled anomalies)',
        'Oceanic_Thermal_Forcing_Availability': 'Fully Available (Standard, PIGL calibrations)',
        'Ice_Sheet_Model_Simulations_Count': 15,
        'Simulation_Status_in_ISMIP6': 'OFFICIAL CORE TIER-1 EXPERIMENT (exp07, exp03, expA4, expA8)',
        'Linear_Interpolation_Permitted': 'N/A (Authentic multi-model ensemble exists)',
        'Operational_Status_for_Phase5': 'APPROVED AS PRIMARY MITIGATION BENCHMARK'
    },
    {
        'Scenario_Designation': 'CMIP6 SSP5-8.5 (ssp585)',
        'Emissions_Pathway_Class': 'Very High Emissions (Updated CMIP6 ECS / Shared Socioeconomic Pathway 5)',
        'Driving_Climate_Models': 'CESM2, UKESM1-0-LL, CNRM-CM6-1',
        'Atmospheric_Forcing_Availability': 'Available via Payne et al. 2021 extension archive',
        'Oceanic_Thermal_Forcing_Availability': 'Available via Payne et al. 2021 extension archive',
        'Ice_Sheet_Model_Simulations_Count': 8,
        'Simulation_Status_in_ISMIP6': 'OFFICIAL CMIP6 EXTENSION (Payne et al. 2021 / Zenodo 4498330)',
        'Linear_Interpolation_Permitted': 'N/A (Authentic simulation exists; separate from RCP8.5)',
        'Operational_Status_for_Phase5': 'APPROVED FOR SECONDARY SENSITIVITY (Do NOT conflate with RCP8.5)'
    },
    {
        'Scenario_Designation': 'CMIP6 SSP1-2.6 (ssp126)',
        'Emissions_Pathway_Class': 'Sustainability Pathway (Updated CMIP6 ECS / Paris Agreement Goal)',
        'Driving_Climate_Models': 'CNRM-CM6-1, CESM2, UKESM1-0-LL',
        'Atmospheric_Forcing_Availability': 'Available via Payne et al. 2021 extension archive',
        'Oceanic_Thermal_Forcing_Availability': 'Available via Payne et al. 2021 extension archive',
        'Ice_Sheet_Model_Simulations_Count': 8,
        'Simulation_Status_in_ISMIP6': 'OFFICIAL CMIP6 EXTENSION (Payne et al. 2021 / Zenodo 4498330)',
        'Linear_Interpolation_Permitted': 'N/A (Authentic simulation exists; separate from RCP2.6)',
        'Operational_Status_for_Phase5': 'APPROVED FOR SECONDARY SENSITIVITY (Do NOT conflate with RCP2.6)'
    },
    {
        'Scenario_Designation': 'CMIP6 SSP2-4.5 / CMIP5 RCP4.5',
        'Emissions_Pathway_Class': 'Middle-of-the-Road / Intermediate Emissions (~4.5 W/m2 by 2100)',
        'Driving_Climate_Models': 'Global CMIP6 GCMs exist at 100–200 km resolution; NO downscaled ISMIP6 suite',
        'Atmospheric_Forcing_Availability': 'UNAVAILABLE (Neither MAR nor RACMO downscaled under ISMIP6 protocol)',
        'Oceanic_Thermal_Forcing_Availability': 'UNAVAILABLE (No ISMIP6 ocean thermal forcing prepared or archived)',
        'Ice_Sheet_Model_Simulations_Count': 0,
        'Simulation_Status_in_ISMIP6': 'NEVER COMMISSIONED OR RUN BY ISMIP6 (Completely Absent)',
        'Linear_Interpolation_Permitted': 'STRICTLY PROHIBITED (Linear interpolation ignores ice-shelf collapse thresholds and non-linear grounding-line dynamics)',
        'Operational_Status_for_Phase5': 'OFFICIALLY DECLARED UNAVAILABLE (Do NOT invent or label synthetic trajectories as native projections)'
    }
]

df_scen_audit = pd.DataFrame(scenarios_audit)
out_csv = os.path.join(TABLES_DIR, 'ismip6_scenario_methodology_audit.csv')
df_scen_audit.to_csv(out_csv, index=False)
print(f"Saved {out_csv} ({len(df_scen_audit)} rows)")

