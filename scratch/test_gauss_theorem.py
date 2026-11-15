import numpy as np

# Create a test grid
Ny, Nx = 100, 100
# Random domain mask
np.random.seed(42)
domain = np.random.rand(Ny, Nx) > 0.4

# Arbitrary fluxes on X faces (Ny, Nx-1) and Y faces (Ny-1, Nx)
fx = np.random.randn(Ny, Nx - 1) * 100.0
fy = np.random.randn(Ny - 1, Nx) * 100.0

# Cell divergence:
# fx[i, j] is flux eastward from (i, j) to (i, j+1)
# fy[i, j] is flux northward from (i+1, j) to (i, j)
div_F = np.zeros((Ny, Nx), dtype=np.float64)
# Eastward flux leaves (i, j), enters (i, j+1)
div_F[:, :-1] += fx
div_F[:, 1:] -= fx
# Northward flux leaves (i+1, j), enters (i, j)
div_F[1:, :] += fy
div_F[:-1, :] -= fy

# Total divergence on domain:
sum_div = np.sum(div_F[domain])

# Boundary faces of domain:
# X faces:
# (i, j) in domain, (i, j+1) NOT in domain -> leaves domain (+fx)
bnd_x_out = fx * (domain[:, :-1] & (~domain[:, 1:]))
# (i, j) NOT in domain, (i, j+1) IN domain -> enters domain (-fx), so outflow is -fx
bnd_x_in = -fx * ((~domain[:, :-1]) & domain[:, 1:])

# Y faces:
# (i+1, j) in domain, (i, j) NOT in domain -> leaves domain northward (+fy)
bnd_y_out = fy * (domain[1:, :] & (~domain[:-1, :]))
# (i+1, j) NOT in domain, (i, j) IN domain -> enters domain northward (-fy), so outflow is -fy
bnd_y_in = -fy * ((~domain[1:, :]) & domain[:-1, :])

# Also boundary of the raster box:
# Col 0: if in domain, entering from outside col -1? fx is 0 outside.
# If domain borders array edge:
edge_col_0 = -0.0 # no flux defined
edge_col_end = 0.0

bnd_sum = np.sum(bnd_x_out) + np.sum(bnd_x_in) + np.sum(bnd_y_out) + np.sum(bnd_y_in)

# Add edge cells of domain touching array boundary:
# Col 0 has incoming flux -fx[:, 0] only if col 0 is entered from col -1 (which doesn't exist)
# But in div_F: div_F[:, 0] received -fx[:, -1]?? No!
# Look at div_F:
# div_F[:, :-1] += fx -> col Nx-1 has NO outflow fx[:, Nx-1]
# div_F[:, 1:] -= fx  -> col 0 has NO inflow fx[:, -1]

# What about faces crossing the domain boundary?
# Let's check difference:
diff = sum_div - bnd_sum
print(f"Discrete Gauss theorem check:")
print(f"  Sum of div_F inside domain: {sum_div:.10f}")
print(f"  Sum of boundary face fluxes: {bnd_sum:.10f}")
print(f"  Difference: {diff:.14e}")
