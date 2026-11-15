import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath('antarctic-ice-volume-prediction')
TABLES_DIR = os.path.join(BASE_DIR, 'reports', 'tables')
os.makedirs(TABLES_DIR, exist_ok=True)

ts_csv = os.path.join(BASE_DIR, 'data', 'processed', 'ismip6', 'ismip6_basin_timeseries_clean.csv')
df_ts = pd.read_csv(ts_csv)

milestone_years = [2030, 2040, 2050, 2075, 2100]
basins = ['Hp-I', 'I-Ipp', 'Ipp-J', 'Domain_A']
scenarios = ['CMIP5_RCP85', 'CMIP5_RCP26']

extreme_drift_models = ['UCIJPL_ISSM', 'JPL1_ISSM', 'DOE_MALI']

sensitivity_rows = []

for scen in scenarios:
    df_scen = df_ts[df_ts['Scenario_Family'] == scen]
    
    for basin in basins:
        df_b = df_scen[df_scen['Basin_ID'] == basin]
        
        for yr in milestone_years:
            df_yr = df_b[df_b['Year'] == yr]
            
            # Group by Model_Key (mean across experiments if multiple)
            mod_means = df_yr.groupby('Model_Key')['VAF_Anomaly_relative_to_Control_km3'].mean()
            
            # Case 1: Full Ensemble
            vals_full = mod_means.values
            n_full = len(vals_full)
            mean_full = np.mean(vals_full)
            med_full = np.median(vals_full)
            std_full = np.std(vals_full, ddof=1) if n_full > 1 else 0
            p16_full = np.percentile(vals_full, 16)
            p84_full = np.percentile(vals_full, 84)
            iqr_full = np.percentile(vals_full, 75) - np.percentile(vals_full, 25)
            
            # Case 2: Excluding UCIJPL ISSM
            mod_no_uci = mod_means[~mod_means.index.isin(['UCIJPL_ISSM'])]
            vals_no_uci = mod_no_uci.values
            n_no_uci = len(vals_no_uci)
            mean_no_uci = np.mean(vals_no_uci)
            med_no_uci = np.median(vals_no_uci)
            std_no_uci = np.std(vals_no_uci, ddof=1) if n_no_uci > 1 else 0
            p16_no_uci = np.percentile(vals_no_uci, 16)
            p84_no_uci = np.percentile(vals_no_uci, 84)
            iqr_no_uci = np.percentile(vals_no_uci, 75) - np.percentile(vals_no_uci, 25)
            
            # Case 3: Excluding All Extreme Drift Models (|drift| > 1000 km3)
            mod_low_drift = mod_means[~mod_means.index.isin(extreme_drift_models)]
            vals_low = mod_low_drift.values
            n_low = len(vals_low)
            mean_low = np.mean(vals_low)
            med_low = np.median(vals_low)
            std_low = np.std(vals_low, ddof=1) if n_low > 1 else 0
            p16_low = np.percentile(vals_low, 16)
            p84_low = np.percentile(vals_low, 84)
            iqr_low = np.percentile(vals_low, 75) - np.percentile(vals_low, 25)
            
            # Deltas
            delta_med_uci = med_no_uci - med_full
            delta_med_all = med_low - med_full
            
            sensitivity_rows.append({
                'Scenario_Family': scen,
                'Basin_ID': basin,
                'Milestone_Year': yr,
                'Full_Ensemble_N': n_full,
                'Full_Mean_km3': round(mean_full, 2),
                'Full_Median_km3': round(med_full, 2),
                'Full_Std_km3': round(std_full, 2),
                'Full_16th_km3': round(p16_full, 2),
                'Full_84th_km3': round(p84_full, 2),
                'Full_IQR_km3': round(iqr_full, 2),
                'Excl_UCIJPL_N': n_no_uci,
                'Excl_UCIJPL_Mean_km3': round(mean_no_uci, 2),
                'Excl_UCIJPL_Median_km3': round(med_no_uci, 2),
                'Excl_UCIJPL_IQR_km3': round(iqr_no_uci, 2),
                'Delta_Median_UCIJPL_km3': round(delta_med_uci, 2),
                'Excl_All_Extreme_N': n_low,
                'Excl_All_Extreme_Mean_km3': round(mean_low, 2),
                'Excl_All_Extreme_Median_km3': round(med_low, 2),
                'Excl_All_Extreme_IQR_km3': round(iqr_low, 2),
                'Delta_Median_All_Extreme_km3': round(delta_med_all, 2),
                'Robustness_Assessment': (
                    'Robust to UCIJPL Exclusion (Median Delta < 25 km3)' if abs(delta_med_uci) < 25 else
                    f'Moderate UCIJPL Sensitivity (Median Delta = {delta_med_uci:+.1f} km3)'
                )
            })

df_sens = pd.DataFrame(sensitivity_rows)
out_csv = os.path.join(TABLES_DIR, 'ismip6_drift_sensitivity.csv')
df_sens.to_csv(out_csv, index=False)
print(f"Saved {out_csv} ({len(df_sens)} rows)")

