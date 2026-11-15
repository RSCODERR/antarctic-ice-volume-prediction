import os, numpy as np, netCDF4 as nc, scipy.ndimage, pandas as pd
import scipy.sparse as sp, scipy.sparse.linalg as spla

NC_UNIFIED = 'antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc'
ds_u = nc.Dataset(NC_UNIFIED)
H_init = np.nan_to_num(np.asarray(ds_u.variables["thickness"][:]), nan=0.0).astype(np.float64)
surface_init = np.nan_to_num(np.asarray(ds_u.variables["surface"][:]), nan=0.0).astype(np.float64)
bed = np.nan_to_num(np.asarray(ds_u.variables["bed"][:]), nan=0.0).astype(np.float64)
driving_stress_init = np.nan_to_num(np.asarray(ds_u.variables["driving_stress"][:]), nan=0.0).astype(np.float64)
smb_clim = np.nan_to_num(np.asarray(ds_u.variables["smb"][:]), nan=0.0).astype(np.float64)
alpha_g_init = np.nan_to_num(np.asarray(ds_u.variables["alpha_grounded"][:]), nan=0.0).astype(np.float64)
alpha_f_init = np.nan_to_num(np.asarray(ds_u.variables["alpha_floating"][:]), nan=0.0).astype(np.float64)
cell_area_wgs84 = np.nan_to_num(np.asarray(ds_u.variables["cell_area_wgs84_m2"][:]), nan=1e6).astype(np.float64)
vx_0761 = np.nan_to_num(np.asarray(ds_u.variables["vx_0761"][:]), nan=0.0).astype(np.float64)
vy_0761 = np.nan_to_num(np.asarray(ds_u.variables["vy_0761"][:]), nan=0.0).astype(np.float64)
ds_u.close()

RHO_ICE = 917.0
RHO_WATER = 1028.0
GRAVITY = 9.81
GLEN_B = 1.42004e8
SPY = 31556926.0

Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
k_scale = np.sqrt((dx * dy) / cell_area_wgs84)
ds_x = dy / k_scale
ds_y = dx / k_scale

grounded_init = (alpha_g_init >= alpha_f_init) & (alpha_g_init > 0) & (H_init > 10.0)
floating_init = (alpha_f_init > alpha_g_init) & (alpha_f_init > 0) & (H_init > 10.0)
ice_mask_init = grounded_init | floating_init
n_active = int(np.sum(grounded_init))

h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)

cell_to_dof = np.full((Ny, Nx), -1, dtype=np.int32)
cell_to_dof[grounded_init] = np.arange(n_active, dtype=np.int32)

mask_x = grounded_init[:, :-1] & grounded_init[:, 1:]
k1_x = cell_to_dof[:, :-1][mask_x]
k2_x = cell_to_dof[:, 1:][mask_x]

mask_y = grounded_init[:-1, :] & grounded_init[1:, :]
k1_y = cell_to_dof[:-1, :][mask_y]
k2_y = cell_to_dof[1:, :][mask_y]

rows_u = np.concatenate([k1_x, k2_x, k1_y, k2_y])
cols_u = np.concatenate([k2_x, k1_x, k2_y, k1_y])
rows_v = rows_u + n_active
cols_v = cols_u + n_active
all_rows = np.concatenate([np.arange(n_active), np.arange(n_active) + n_active, rows_u, rows_v])
all_cols = np.concatenate([np.arange(n_active), np.arange(n_active) + n_active, cols_u, cols_v])

c_bed_vec = np.full(n_active, 8.168e6, dtype=np.float64)

def solve_picard_custom(H_in, s_in, max_iter=6, warm_u=None, warm_v=None):
    s_eval = scipy.ndimage.gaussian_filter(s_in, sigma=1.0)
    ds_dy, ds_dx = np.gradient(s_eval, -dy, dx)
    slope_mag = np.sqrt(ds_dx**2 + ds_dy**2)
    trig_fac = 1.0 / np.sqrt(1.0 + slope_mag**2)

    bu_grid = -RHO_ICE * GRAVITY * H_in * ds_dx * trig_fac
    bv_grid = -RHO_ICE * GRAVITY * H_in * ds_dy * trig_fac
    bu = bu_grid[grounded_init]
    bv = bv_grid[grounded_init]

    td_mag = np.sqrt(bu**2 + bv**2)
    fac_reg = 1.0 / np.sqrt(1.0 + (td_mag / (350e3))**2)
    bu *= fac_reg
    bv *= fac_reg
    rhs_vec = np.concatenate([bu, bv])

    Hf_x = 0.5 * (H_in[:, :-1][mask_x] + H_in[:, 1:][mask_x])
    Hf_y = 0.5 * (H_in[:-1, :][mask_y] + H_in[1:, :][mask_y])

    if warm_u is not None and warm_v is not None:
        wu = warm_u[grounded_init] if warm_u.shape == (Ny, Nx) else warm_u
        wv = warm_v[grounded_init] if warm_v.shape == (Ny, Nx) else warm_v
        u_act = np.clip(wu, -5000.0, 5000.0) / SPY
        v_act = np.clip(wv, -5000.0, 5000.0) / SPY
    else:
        u_sia = (td_mag / c_bed_vec)**3.0
        u_act = bu / (td_mag + 1e-6) * np.minimum(u_sia, 500.0 / SPY)
        v_act = bv / (td_mag + 1e-6) * np.minimum(u_sia, 500.0 / SPY)

    u_grid = np.zeros((Ny, Nx), dtype=np.float64)
    v_grid = np.zeros((Ny, Nx), dtype=np.float64)

    for it in range(1, max_iter + 1):
        u_grid[grounded_init] = u_act
        v_grid[grounded_init] = v_act

        du_dy, du_dx = np.gradient(u_grid, -dy, dx)
        dv_dy, dv_dx = np.gradient(v_grid, -dy, dx)
        dxy = 0.5 * (du_dy + dv_dx)
        eps_e = np.sqrt(du_dx**2 + dv_dy**2 + du_dx * dv_dy + dxy**2 + 1e-10)
        nu_grid = 0.5 * GLEN_B * (eps_e ** (-2.0 / 3.0))

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
        diag_u += alpha_g_init[grounded_init] * beta_b
        diag_v += alpha_g_init[grounded_init] * beta_b

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

    u_grid = np.nan_to_num(vx_0761, nan=0.0).copy()
    v_grid = np.nan_to_num(vy_0761, nan=0.0).copy()
    u_grid[grounded_init] = u_act * SPY
    v_grid[grounded_init] = v_act * SPY
    return u_grid, v_grid

# Solve initial state
print("Solving initial velocity...")
u_curr, v_curr = solve_picard_custom(H_init, surface_init, max_iter=6)

# Run year 2000
H_hist = H_init.copy()
grd_hist = grounded_init.copy()
flt_hist = floating_init.copy()

for yr in [2000, 2001]:
    if yr > 2000:
        s_hist_OLD = np.where(grd_hist, bed + H_hist, (1.0 - RHO_ICE / RHO_WATER) * H_hist)
        s_hist_NEW = surface_init + np.where(grd_hist, H_hist - H_init, (1.0 - RHO_ICE / RHO_WATER) * (H_hist - H_init))
        
        # Check max difference in s
        print(f"Max diff in s between OLD and NEW: {np.max(np.abs(s_hist_OLD - s_hist_NEW)):.1f} m")
        
        # Test Picard solve with NEW surface
        u_curr, v_curr = solve_picard_custom(H_hist, s_hist_NEW, max_iter=6, warm_u=u_curr[grounded_init], warm_v=v_curr[grounded_init])
    
    ann_gl = 0.0
    ann_cg = 0.0
    for st in range(10):
        act = grd_hist | flt_hist
        u_fx = 0.5 * (u_curr[:, :-1] + u_curr[:, 1:])
        h_up_x = np.where(u_fx > 0, H_hist[:, :-1], H_hist[:, 1:])
        fx = h_up_x * u_fx * 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])

        v_fy = 0.5 * (v_curr[:-1, :] + v_curr[1:, :])
        h_up_y = np.where(v_fy > 0, H_hist[1:, :], H_hist[:-1, :])
        fy = h_up_y * v_fy * 0.5 * (ds_y[:-1, :] + ds_y[1:, :])

        div_F = np.zeros((Ny, Nx), dtype=np.float64)
        div_F[:, :-1] += fx; div_F[:, 1:] -= fx
        div_F[1:, :] += fy; div_F[:-1, :] -= fy

        gl_x = np.sum(fx[grd_hist[:, :-1] & flt_hist[:, 1:]]) - np.sum(fx[flt_hist[:, :-1] & grd_hist[:, 1:]])
        gl_y = np.sum(fy[grd_hist[1:, :] & flt_hist[:-1, :]]) - np.sum(fy[flt_hist[1:, :] & grd_hist[:-1, :]])
        F_gl_st = (gl_x + gl_y) * RHO_ICE * 1e-12

        not_ice = ~act
        cg_x = np.sum(fx[grd_hist[:, :-1] & not_ice[:, 1:]]) - np.sum(fx[not_ice[:, :-1] & grd_hist[:, 1:]])
        cg_y = np.sum(fy[grd_hist[1:, :] & not_ice[:-1, :]]) - np.sum(fy[not_ice[1:, :] & grd_hist[:-1, :]])
        F_cg_st = (cg_x + cg_y) * RHO_ICE * 1e-12

        ann_gl += F_gl_st * 0.1
        ann_cg += F_cg_st * 0.1

        dH = 0.1 * (smb_clim / RHO_ICE - div_F / cell_area_wgs84)
        H_hist = H_hist + dH
    
    print(f"Year {yr}: GL Flux = {ann_gl:.1f} Gt/yr, Calving = {ann_cg:.1f} Gt/yr")
