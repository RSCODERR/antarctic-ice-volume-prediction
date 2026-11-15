import os, sys
if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')
sys.path.insert(0, '.')
sys.path.insert(0, 'src')

import numpy as np
import netCDF4 as nc
from scipy.ndimage import gaussian_filter1d
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.state import IceState
from physics.ssa_solver import SSASolver
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter
from physics.basal_drag import BasalDrag

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

def build_domain(cfg):
    pts = cfg['waypoints']
    N_raw = cfg['n_pts']
    t_pts = np.linspace(0, 1, len(pts))
    t_eval = np.linspace(0, 1, N_raw)
    x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
    y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])

    cols = np.clip(np.round((x_eval - xs[0]) / dx).astype(int), 0, len(xs)-1)
    rows = np.clip(np.round((ys[0] - y_eval) / abs(dy)).astype(int), 0, len(ys)-1)

    r_min = max(0, rows.min() - 15)
    r_max = min(len(ys)-1, rows.max() + 15)
    c_min = max(0, cols.min() - 15)
    c_max = min(len(xs)-1, cols.max() + 15)

    sub_surf = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
    sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
    sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
    sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]

    thalweg_r = []
    thalweg_c = []
    for r_target, c_target in zip(rows, cols):
        r_loc = r_target - r_min
        c_loc = c_target - c_min
        r0 = max(0, r_loc - 8)
        r1 = min(sub_thick.shape[0], r_loc + 9)
        c0 = max(0, c_loc - 8)
        c1 = min(sub_thick.shape[1], c_loc + 9)
        w_thick = np.array(sub_thick[r0:r1, c0:c1])
        w_mask = np.array(sub_mask[r0:r1, c0:c1])
        w_thick[w_mask == 1] = -1.0
        w_thick[w_mask == 0] = -1.0
        if np.all(w_thick < 0):
            thalweg_r.append(r_target)
            thalweg_c.append(c_target)
        else:
            max_idx = np.unravel_index(np.nanargmax(w_thick), w_thick.shape)
            thalweg_r.append(r_min + r0 + max_idx[0])
            thalweg_c.append(c_min + c0 + max_idx[1])

    rel_r = np.array(thalweg_r) - r_min
    rel_c = np.array(thalweg_c) - c_min

    thick_raw = np.array([float(sub_thick[r, c]) for r, c in zip(rel_r, rel_c)])
    bed_raw = np.array([float(sub_bed[r, c]) for r, c in zip(rel_r, rel_c)])
    surf_raw = np.array([float(sub_surf[r, c]) for r, c in zip(rel_r, rel_c)])

    peak_idx = int(np.argmax(surf_raw[:15]))
    term_idx = int(np.argmin(surf_raw))
    if term_idx <= peak_idx:
        term_idx = len(surf_raw) - 1

    N_actual = term_idx - peak_idx + 1
    thick_cut = thick_raw[peak_idx:term_idx+1].copy()
    bed_cut = bed_raw[peak_idx:term_idx+1].copy()

    sigma_cells = 3.0
    bed_s = gaussian_filter1d(bed_cut, sigma=sigma_cells, mode='nearest')
    thick_s = gaussian_filter1d(thick_cut, sigma=sigma_cells, mode='nearest')
    thick_s = np.maximum(thick_s, 50.0)

    x_centres = np.arange(N_actual, dtype=np.float64) * CONST.domain_dx + 0.5 * CONST.domain_dx
    width = np.full(N_actual, cfg['width_m'], dtype=np.float64)

    domain = FlowlineDomain(
        x_centres=x_centres,
        bed=bed_s,
        width=width,
        H_init=thick_s,
        name=cfg['name'],
        source='Thalweg'
    )
    return domain

cfg_dry = {
    'name': 'Drygalski Glacier System',
    'basin': 'Ipp-J',
    'waypoints': [
        (-2456905.7, 1339548.5),
        (-2442512.2, 1353906.6),
        (-2428039.1, 1368129.7)
    ],
    'width_m': 6200.0,
    'n_pts': 80,
    'obs_u_gl': 305.0,
    'obs_sigma': 18.03,
    'smb_yr': 0.35,
    'gate_id': 'GATE_IPJ_DRY'
}

cfg_flask = {
    'name': 'Flask / Leppard Glacier System',
    'basin': 'Ipp-J',
    'waypoints': [
        (-2388233.8, 1201156.5),
        (-2370483.5, 1223497.8),
        (-2352885.6, 1245037.2)
    ],
    'width_m': 7100.0,
    'n_pts': 75,
    'obs_u_gl': 310.0,
    'obs_sigma': 18.03,
    'smb_yr': 0.40,
    'gate_id': 'GATE_IPJ_03'
}

cb_frozen = 8.168e+06
basal = BasalDrag(CONST, C_bed=cb_frozen)

# 1. Inspect Drygalski diagnostic solve
dom_dry = build_domain(cfg_dry)
st_dry = dom_dry.initial_state()

class DetailedTracker(SSASolver):
    def solve_trace(self, state, u_upstream=0.0):
        N_gr = state.gl_cell + 1
        H = state.H[:N_gr].copy()
        bed = state.bed[:N_gr].copy()
        width = state.width[:N_gr].copy()
        dx = state.dx
        surf = H + bed
        ds_dx = np.zeros(N_gr, dtype=np.float64)
        ds_dx[:-1] = (surf[1:] - surf[:-1]) / dx
        ds_dx[-1] = ds_dx[-2]

        tau_d = np.maximum(0.0, -ds_dx) * self.const.rho_ice * self.const.g * H
        u_est = (np.maximum(tau_d, 1.0) / self.basal.C_bed) ** (1.0 / self.basal.m)
        u = np.clip(u_est, 1e-4 / self.const.yr_to_s, 2000.0 / self.const.yr_to_s)
        if u_upstream is not None:
            u[0] = u_upstream

        history = []
        for k in range(self.max_iter):
            du_dx = self.rheology.strain_rate_from_velocity(u, dx)
            nu_eff = self.rheology.effective_viscosity(du_dx)
            beta_b = self.basal.beta_linearised(u)
            beta_lat = self.lateral.beta_lateral(u, width, H)
            u_solve = self._solve_tridiagonal(H, nu_eff, beta_b, beta_lat, ds_dx, width, dx, N_gr, u_upstream)
            u_new = self.omega * u_solve + (1.0 - self.omega) * u
            norm_diff = np.linalg.norm(u_new - u)
            norm_ref = np.linalg.norm(u) + self.u_scale * np.sqrt(N_gr)
            res = norm_diff / norm_ref
            history.append((k + 1, res))
            u = u_new
            if res <= self.tol:
                break
        return u, history

tracker = DetailedTracker(CONST, basal=basal, tol=1e-4, max_iter=80)
u_dry, hist_dry = tracker.solve_trace(st_dry, u_upstream=0.0)

print(f"Drygalski Diagnostic solve: Total iters={len(hist_dry)}, Final res={hist_dry[-1][1]:.6e}")
print("Iterations 1 to 5 and 75 to 80:")
for it, res in hist_dry[:5]:
    print(f"  Iter {it:2d}: res = {res:.6e}")
for it, res in hist_dry[74:]:
    print(f"  Iter {it:2d}: res = {res:.6e}")

res_vals = [r for it, r in hist_dry]
ratios = [res_vals[i]/res_vals[i-1] for i in range(1, len(res_vals))]
print(f"Mean contraction ratio (last 10 iters): {np.mean(ratios[-10:]):.4f}")

# 2. Prognostic step audit for Flask and Drygalski
print("\n--- Auditing Prognostic Forward Steps ---")
dt = 0.02 * CONST.yr_to_s
n_steps = 250
smb_conv = SMBConverter(CONST)

for name, cfg in [('Flask', cfg_flask), ('Drygalski', cfg_dry)]:
    dom = build_domain(cfg)
    st = dom.initial_state()
    ssa = SSASolver(CONST, basal=basal, tol=1e-4, max_iter=80)
    fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)
    smb_m_s = smb_conv.from_m_ice_yr(np.full(dom.N, cfg['smb_yr']))
    
    cur_st = st
    unconv_steps = []
    
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for step in range(n_steps):
            t_yr = step * 0.02
            cur_st, diag_step = fv.step(cur_st, smb_m_s=smb_m_s, dt=dt, u_upstream=0.0)
            if not diag_step.ssa_converged:
                unconv_steps.append((step, t_yr, diag_step.ssa_picard_residual))
    
    print(f"\n{name} Glacier: {len(unconv_steps)} unconverged forward steps out of {n_steps} ({(len(unconv_steps)/n_steps)*100:.1f}%)")
    if unconv_steps:
        step_indices = [s[0] for s in unconv_steps]
        res_list = [s[2] for s in unconv_steps]
        print(f"  Step index range: {min(step_indices)} to {max(step_indices)}")
        print(f"  Residual range: min = {min(res_list):.6e}, max = {max(res_list):.6e}, median = {np.median(res_list):.6e}")
        print(f"  First 5 unconverged steps: {unconv_steps[:5]}")
        print(f"  Last 5 unconverged steps: {unconv_steps[-5:]}")
