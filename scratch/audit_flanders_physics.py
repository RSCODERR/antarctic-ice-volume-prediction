import numpy as np

# Flanders Bay parameters at cell 14 (peak driving stress)
H = 241.2 # m
W = 3800.0 # m
slope = 0.293 # 29.3%
rho_i = 917.0
g = 9.81
tau_d = rho_i * g * H * slope
print(f"Driving stress at cell 14: tau_d = {tau_d:.1f} Pa ({tau_d/1e3:.1f} kPa)")

# Basal drag coefficient
C_bed = 1.0e7
m = 1.0/3.0
A = 3.5e-25
yr_to_s = 31557600.0

# If tau_b balances tau_d alone:
u_unassisted = (tau_d / C_bed)**(1.0/m) # m/s
print(f"Unassisted sliding velocity: {u_unassisted * yr_to_s:.1f} m/yr")

# Current lateral drag formula: f_lat = 2 * tau_wall / W
# tau_wall = (5 * u / (A * W))^(1/3)
u_sim = 4963.8 / yr_to_s # m/s
tau_w = (5.0 * u_sim / (A * W))**(1.0/3.0)
f_lat_current = 2.0 * tau_w / W
print(f"At u = 4964 m/yr:")
print(f"  Wall shear stress tau_w = {tau_w/1e3:.1f} kPa")
print(f"  Current lateral force term (2 tau_w / W) = {f_lat_current:.2f} Pa ({f_lat_current/1e3:.4f} kPa)")

# Dimensional lateral drag: f_lat_dim = (2 H / W) * tau_w
f_lat_corrected = (2.0 * H / W) * tau_w
print(f"  Corrected plan-area lateral force ((2H/W) * tau_w) = {f_lat_corrected:.1f} Pa ({f_lat_corrected/1e3:.1f} kPa)")

# What if tau_d = 60 kPa (typical low-gradient fjord tongue where s drops 100m over 10km, slope = 0.01)?
tau_d_fjord = rho_i * g * 300.0 * 0.01
u_fjord = (tau_d_fjord / C_bed)**(1.0/m)
print(f"\nIn a low-gradient fjord tongue (slope=1%, H=300m, tau_d={tau_d_fjord/1e3:.1f} kPa):")
print(f"  Unassisted sliding velocity = {u_fjord * yr_to_s:.1f} m/yr")

