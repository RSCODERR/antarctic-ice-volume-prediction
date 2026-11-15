import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df_time = pd.read_csv("reports/tables/stage5_0_timestep_sensitivity.csv")
print("=== FULL TIMESTEP SENSITIVITY TABLE ===")
print(df_time)

df_pilot = pd.read_csv("reports/tables/stage5_0_historical_pilot_results.csv")
print("\n=== FULL HISTORICAL PILOT TABLE ===")
print(df_pilot)

df_mass = pd.read_csv("reports/tables/stage5_0_mass_conservation_tests.csv")
print("\n=== FULL MASS CONSERVATION TESTS TABLE ===")
print(df_mass)
