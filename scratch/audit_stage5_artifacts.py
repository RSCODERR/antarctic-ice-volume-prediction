import os
import netCDF4 as nc
import numpy as np
import pandas as pd

# Load Stage 5.0 tables
tbl_dir = "reports/tables"
df_mass = pd.read_csv(os.path.join(tbl_dir, "stage5_0_mass_conservation_tests.csv"))
df_time = pd.read_csv(os.path.join(tbl_dir, "stage5_0_timestep_sensitivity.csv"))
df_pilot = pd.read_csv(os.path.join(tbl_dir, "stage5_0_historical_pilot_results.csv"))
df_lim = pd.read_csv(os.path.join(tbl_dir, "stage5_0_failure_and_limitation_register.csv"))
df_force = pd.read_csv(os.path.join(tbl_dir, "stage5_0_forcing_inventory.csv"))
df_state = pd.read_csv(os.path.join(tbl_dir, "stage5_0_state_variable_registry.csv"))

print("=== MASS CONSERVATION LEDGER ===")
print(df_mass[["Step_Number", "Time_yr", "Initial_Grounded_Mass_Gt", "Grounded_SMB_Contribution_Gt", "Grounding_Line_Transfer_Gt", "Grounded_Calving_Loss_Gt", "Ungrounded_Cell_Count", "Ungrounded_Mass_Transfer_Gt", "Final_Grounded_Mass_Gt", "Numerical_Residual_Gt", "Conservation_Check"]])

print("\n=== TIMESTEP SENSITIVITY ===")
print(df_time)

print("\n=== HISTORICAL PILOT ===")
print(df_pilot[["Historical_Year", "RACMO_Grounded_SMB_Gt_yr", "Total_Grounded_Marine_Loss_Gt_yr", "Grounded_Net_Mass_Balance_Gt_yr", "Cumulative_Modeled_Grounded_Mass_Loss_Gt", "Ungrounded_Cells_Annual", "Regrounded_Cells_Annual", "Independent_IMBIE3_Mass_Balance_Gt_yr", "Independent_IMBIE3_Uncertainty_Gt_yr", "Model_vs_IMBIE3_Difference_Gt_yr"]])
