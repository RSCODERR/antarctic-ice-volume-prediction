import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.ssa_solver import SSASolver

dx = 500.0
N = 10
x = np.arange(N) * dx + 0.5 * dx
bed = 500.0 - 0.005 * x
H = np.full(N, 500.0)
width = np.full(N, 15000.0)

domain = FlowlineDomain(x, bed, width, H, name="ramp_test", source="test")
state = domain.initial_state()

ssa = SSASolver(CONST, tol=1e-5, max_iter=2)
# Let's inspect step by step
surf = state.H + state.bed
ds_dx = np.zeros(N)
ds_dx[:-1] = (surf[1:] - surf[:-1]) / dx
ds_dx[-1] = ds_dx[-2]
print("ds_dx:", ds_dx)

# Initial guess in SSASolver:
tau_d = np.maximum(0.0, -ds_dx) * CONST.rho_ice * CONST.g * H
print("tau_d:", tau_d)
u_est = (np.maximum(tau_d, 1.0) / ssa.basal.C_bed) ** (1.0 / ssa.basal.m)
print("u_est [m/s]:", u_est)
print("u_est [m/yr]:", u_est * CONST.yr_to_s)

# Solve tridiagonal
du_dx = ssa.rheology.strain_rate_from_velocity(u_est, dx)
nu_eff = ssa.rheology.effective_viscosity(du_dx)
beta_b = ssa.basal.beta_linearised(u_est)
beta_lat = ssa.lateral.beta_lateral(u_est, width)
print("beta_b:", beta_b)
print("beta_lat:", beta_lat)

u_solve = ssa._solve_tridiagonal(H, nu_eff, beta_b, beta_lat, ds_dx, width, dx, N, None)
print("u_solve [m/s]:", u_solve)
print("u_solve [m/yr]:", u_solve * CONST.yr_to_s)

