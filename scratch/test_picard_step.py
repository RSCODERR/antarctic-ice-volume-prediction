import os, numpy as np, netCDF4 as nc, scipy.ndimage, scipy.sparse as sp, scipy.sparse.linalg as spla

NC_UNIFIED = 'antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc'
ds_u = nc.Dataset(NC_UNIFIED)
H_init = ds_u.variables['thickness'][:].astype(np.float64)
surface_init = ds_u.variables['surface'][:].astype(np.float64)
ag = ds_u.variables['alpha_grounded'][:].astype(np.float64)
af = ds_u.variables['alpha_floating'][:].astype(np.float64)
cell_area = ds_u.variables['cell_area_wgs84_m2'][:].astype(np.float64)
vx_0761 = np.nan_to_num(ds_u.variables['vx_0761'][:].astype(np.float64), nan=0.0)
vy_0761 = np.nan_to_num(ds_u.variables['vy_0761'][:].astype(np.float64), nan=0.0)
ds_u.close()

grd = (ag >= af) & (ag > 0) & (H_init > 10.0)
flt = (af > ag) & (af > 0) & (H_init > 10.0)
n_active = int(np.sum(grd))

Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
SPY = 31556926.0

# Precompute DOF maps and face sparsity patterns
cell_to_dof = np.full((Ny, Nx), -1, dtype=np.int32)
cell_to_dof[grd] = np.arange(n_active, dtype=np.int32)

mask_x = grd[:, :-1] & grd[:, 1:]
k1_x = cell_to_dof[:, :-1][mask_x]
k2_x = cell_to_dof[:, 1:][mask_x]

mask_y = grd[:-1, :] & grd[1:, :]
k1_y = cell_to_dof[:-1, :][mask_y]
k2_y = cell_to_dof[1:, :][mask_y]

rows_u = np.concatenate([k1_x, k2_x, k1_y, k2_y])
cols_u = np.concatenate([k2_x, k1_x, k2_y, k1_y])
rows_v = rows_u + n_active
cols_v = cols_u + n_active
all_rows = np.concatenate([np.arange(n_active), np.arange(n_active) + n_active, rows_u, rows_v])
all_cols = np.concatenate([np.arange(n_active), np.arange(n_active) + n_active, cols_u, cols_v])

c_bed_vec = np.full(n_active, 8.168e6, dtype=np.float64)

# Test Picard solve with 3 iterations
s_eval = scipy.ndimage.gaussian_filter(surface_init, sigma=1.0)
ds_dy, ds_dx = np.gradient(s_eval, -dy, dx)
slope_mag = np.sqrt(ds_dx**2 + ds_dy**2)
trig_fac = 1.0 / np.sqrt(1.0 + slope_mag**2)

bu_grid = -917.0 * 9.81 * H_init * ds_dx * trig_fac
bv_grid = -917.0 * 9.81 * H_init * ds_dy * trig_fac
bu = bu_grid[grd]
bv = bv_grid[grd]

td_mag = np.sqrt(bu**2 + bv**2)
fac_reg = 1.0 / np.sqrt(1.0 + (td_mag / (350e3))**2)
bu *= fac_reg
bv *= fac_reg
rhs_vec = np.concatenate([bu, bv])

Hf_x = 0.5 * (H_init[:, :-1][mask_x] + H_init[:, 1:][mask_x])
Hf_y = 0.5 * (H_init[:-1, :][mask_y] + H_init[1:, :][mask_y])

u_act = np.clip(bu / (td_mag + 1e-6) * np.minimum((td_mag / c_bed_vec)**3.0, 500.0 / SPY), -5000.0/SPY, 5000.0/SPY)
v_act = np.clip(bv / (td_mag + 1e-6) * np.minimum((td_mag / c_bed_vec)**3.0, 500.0 / SPY), -5000.0/SPY, 5000.0/SPY)

u_grid = np.zeros((Ny, Nx), dtype=np.float64)
v_grid = np.zeros((Ny, Nx), dtype=np.float64)

for it in range(1, 4):
    u_grid[grd] = u_act
    v_grid[grd] = v_act

    dudx = (u_grid[:, 1:] - u_grid[:, :-1]) / dx
    dvdy = (v_grid[:-1, :] - v_grid[1:, :]) / dy
    dudy = (u_grid[:-1, :] - u_grid[1:, :]) / dy
    dvdx = (v_grid[:, 1:] - v_grid[:, :-1]) / dx
    strain_xy = 0.5 * (dudy + dvdx)

    exx = np.zeros((Ny, Nx), dtype=np.float64)
    eyy = np.zeros((Ny, Nx), dtype=np.float64)
    exy = np.zeros((Ny, Nx), dtype=np.float64)
    exx[:, :-1] += 0.5 * dudx; exx[:, 1:] += 0.5 * dudx
    eyy[:-1, :] += 0.5 * dvdy; eyy[1:, :] += 0.5 * dvdy
    exy[:-1, :-1] += 0.25 * strain_xy; exy[:-1, 1:] += 0.25 * strain_xy
    exy[1:, :-1] += 0.25 * strain_xy; exy[1:, 1:] += 0.25 * strain_xy

    e_eff = np.sqrt(exx[grd]**2 + eyy[grd]**2 + exx[grd]*eyy[grd] + exy[grd]**2 + 1e-20)
    nu_grid = np.zeros((Ny, Nx), dtype=np.float64)
    nu_grid[grd] = 0.5 * 1.42004e8 * (e_eff ** (-2.0 / 3.0))

    nu_x = 0.5 * (nu_grid[:, :-1][mask_x] + nu_grid[:, 1:][mask_x])
    nu_y = 0.5 * (nu_grid[:-1, :][mask_y] + nu_grid[1:, :][mask_y])

    Kx = 4.0 * Hf_x * nu_x / (dx * dx)
    Mx = 1.0 * Hf_x * nu_x / (dx * dx)
    Ky = 1.0 * Hf_y * nu_y / (dy * dy)
    My = 4.0 * Hf_y * nu_y / (dy * dy)

    diag_u = np.zeros(n_active, dtype=np.float64)
    diag_v = np.zeros(n_active, dtype=np.float64)
    np.add.at(diag_u, k1_x, Kx); np.add.at(diag_u, k2_x, Kx)
    np.add.at(diag_v, k1_x, Mx); np.add.at(diag_v, k2_x, Mx)
    np.add.at(diag_u, k1_y, Ky); np.add.at(diag_u, k2_y, Ky)
    np.add.at(diag_v, k1_y, My); np.add.at(diag_v, k2_y, My)

    beta_b = c_bed_vec * (u_act**2 + v_act**2 + (1.0 / SPY)**2)**(-1.0 / 3.0)
    diag_u += ag[grd] * beta_b
    diag_v += ag[grd] * beta_b

    vals_u = np.concatenate([-Kx, -Kx, -Ky, -Ky])
    vals_v = np.concatenate([-Mx, -Mx, -My, -My])
    all_vals = np.concatenate([diag_u, diag_v, vals_u, vals_v])
    A = sp.coo_matrix((all_vals, (all_rows, all_cols)), shape=(2 * n_active, 2 * n_active)).tocsr()

    diag_all = np.concatenate([diag_u, diag_v])
    M_inv = sp.diags(1.0 / np.maximum(diag_all, 1e-10), 0, shape=(2 * n_active, 2 * n_active), format='csr')

    sol, _ = spla.cg(A, rhs_vec, M=M_inv, maxiter=30, atol=1e-3)
    u_cand = np.clip(sol[:n_active], -5000.0 / SPY, 5000.0 / SPY)
    v_cand = np.clip(sol[n_active:], -5000.0 / SPY, 5000.0 / SPY)

    u_act = 0.5 * u_cand + 0.5 * u_act
    v_act = 0.5 * v_cand + 0.5 * v_act
    spd = np.sqrt(u_act**2 + v_act**2) * SPY
    print(f'Iter {it}: Mean speed = {np.mean(spd):.1f} m/yr, Max speed = {np.max(spd):.1f} m/yr')
