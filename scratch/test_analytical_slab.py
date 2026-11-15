import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np
from src.physics.ssa_2d.constants import SSA2DConstants

def solve_slab():
    alpha = 0.005 # surface slope (5 m/km)
    H0 = 600.0   # uniform thickness
    C_bed = 5.0e6 # Pa (m/s)^(-1/3)
    const = SSA2DConstants(C_bed=C_bed)

    tau_d = const.rho_ice * const.g * H0 * alpha
    u_analytical = (tau_d / C_bed) ** 3.0

    print(f"Driving stress tau_d: {tau_d:.2f} Pa")
    print(f"Analytical velocity: {u_analytical:.6e} m/s ({u_analytical * const.sec_per_year:.3f} m/a)")

    u = 0.1 / const.sec_per_year
    for it in range(50):
        beta = C_bed * (u**2 + const.u_0**2)**(-1.0 / 3.0)
        u_new = tau_d / beta
        diff = abs(u_new - u) * const.sec_per_year
        u = 0.6 * u_new + 0.4 * u
        if it < 10 or it % 5 == 0:
            print(f"Iter {it+1:02d}: u = {u*const.sec_per_year:.4f} m/a, diff = {diff:.4e} m/a")
        if diff < 1e-5:
            print(f"Converged at iter {it+1}: u = {u:.6e} m/s, err = {abs(u - u_analytical)/u_analytical:.2e}")
            break

solve_slab()
