import sys, os
os.chdir('antarctic-ice-volume-prediction')
sys.path.insert(0, '.')
sys.path.insert(0, 'src')

import numpy as np
import netCDF4 as nc
from scipy.ndimage import gaussian_filter1d
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.ssa_solver import SSASolver, SSAResult
from physics.continuity import FVContinuitySolver
from physics.smb import SMBConverter
from physics.basal_drag import BasalDrag

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx_grid = 500.0

cfg = {
    'name': 'Ryder / Bertram Glacier System (Palmer Land West)',
    'basin': 'Hp-I',
    'waypoints': [
        (-1820000.0, 820000.0),
        (-1860000.0, 785000.0),
        (-1907000.0, 745000.0)
    ],
    'width_m': 12400.0,
    'n_pts': 105,
    'smb_ice_yr': 0.40,
    'obs_velocity_gl': 385.0
}

pts = cfg['waypoints']
N_raw = cfg['n_pts']
t_pts = np.linspace(0, 1, len(pts))
t_eval = np.linspace(0, 1, N_raw)
x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])

cols = np.clip(np.round((x_eval - xs[0]) / dx_grid).astype(int), 0, len(xs)-1)
rows = np.clip(np.round((ys[0] - y_eval) / dx_grid).astype(int), 0, len(ys)-1)

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

peak_idx = int(np.argmax(surf_raw[:10]))
term_idx = int(np.argmin(surf_raw))
if term_idx <= peak_idx:
    term_idx = len(surf_raw) - 1

N_actual = term_idx - peak_idx + 1
thick_cut = thick_raw[peak_idx:term_idx+1].copy()
bed_cut = bed_raw[peak_idx:term_idx+1].copy()
surf_cut = surf_raw[peak_idx:term_idx+1].copy()

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
    name='FL_HPI_01',
    source='BedMachine_V4.1_Aligned_Thalweg_Smoothed'
)
state = domain.initial_state()

cb_opt = 8.167e+06
basal = BasalDrag(CONST, C_bed=cb_opt)

class InstrumentSSASolver(SSASolver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_iter_residuals = []

    def solve(self, state, u_init=None, u_upstream=None, use_lateral=True):
        self.last_iter_residuals = []
        g = state.gl_cell
        N_gr = g + 1
        H = state.H[:N_gr].copy()
        bed = state.bed[:N_gr].copy()
        width = state.width[:N_gr].copy()
        dx = state.dx
        surf = H + bed
        ds_dx = np.zeros(N_gr, dtype=np.float64)
        ds_dx[:-1] = (surf[1:] - surf[:-1]) / dx
        ds_dx[-1] = ds_dx[-2]

        if u_init is not None:
            u = u_init[:N_gr].copy()
        else:
            tau_d = np.maximum(0.0, -ds_dx) * self.const.rho_ice * self.const.g * H
            u_est = (np.maximum(tau_d, 1.0) / self.basal.C_bed) ** (1.0 / self.basal.m)
            u = np.clip(u_est, 1e-4 / self.const.yr_to_s, 2000.0 / self.const.yr_to_s)

        residual = np.inf
        converged = False

        for k in range(self.max_iter):
            du_dx = self.rheology.strain_rate_from_velocity(u, dx)
            nu_eff = self.rheology.effective_viscosity(du_dx)
            beta_b = self.basal.beta_linearised(u)
            if use_lateral:
                beta_lat = self.lateral.beta_lateral(u, width, H)
            else:
                beta_lat = np.zeros(N_gr, dtype=np.float64)

            u_solve = self._solve_tridiagonal(
                H, nu_eff, beta_b, beta_lat, ds_dx, width, dx, N_gr, u_upstream
            )
            u_new = self.omega * u_solve + (1.0 - self.omega) * u

            norm_diff = np.linalg.norm(u_new - u)
            norm_ref = np.linalg.norm(u) + self.u_scale * np.sqrt(N_gr)
            residual = norm_diff / norm_ref
            self.last_iter_residuals.append(float(residual))
            u = u_new

            if residual <= self.tol:
                converged = True
                break

        u_full = np.full(state.N, np.nan, dtype=np.float64)
        nu_full = np.full(state.N, np.nan, dtype=np.float64)
        u_full[:N_gr] = u
        nu_full[:N_gr] = self.rheology.effective_viscosity(
            self.rheology.strain_rate_from_velocity(u, dx)
        )

        return SSAResult(
            u=u_full,
            nu_eff=nu_full,
            n_iter=k + 1,
            residual=float(residual),
            converged=converged,
        )

ssa = InstrumentSSASolver(CONST, basal=basal, tol=1e-4, max_iter=80)
smb_conv = SMBConverter(CONST)
fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)

dt = 0.02 * CONST.yr_to_s
n_steps = 250
smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, cfg['smb_ice_yr']))

cur_state = state
unconverged_steps = []

import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for step in range(n_steps):
        t_start_yr = step * 0.02
        t_end_yr = (step + 1) * 0.02
        m_before = cur_state.compute_grounded_mass_kg()
        cur_state, diag = fv.step(cur_state, smb_m_s=smb_m_s, dt=dt, u_upstream=0.0)
        m_after = cur_state.compute_grounded_mass_kg()
        
        if not diag.ssa_converged:
            res_history = ssa.last_iter_residuals
            step_res = (m_after - m_before) - (diag.Mdot_SMB * dt - diag.Q_GL * CONST.rho_ice * dt + diag.dM_boundary)
            unconverged_steps.append({
                'step_index': step,
                't_start_yr': t_start_yr,
                't_end_yr': t_end_yr,
                't_start_s': step * dt,
                't_end_s': (step + 1) * dt,
                'n_iter': diag.ssa_n_iter,
                'init_picard_res': res_history[0],
                'final_picard_res': diag.ssa_picard_residual,
                'res_history': res_history,
                'iter_limit_reached': (diag.ssa_n_iter == 80),
                'step_mass_residual_kg': step_res,
                'step_diag_residual_kg': diag.residual,
                'gl_cell': cur_state.gl_cell,
                'gl_frac': cur_state.gl_frac
            })

print(f"Total unconverged steps found: {len(unconverged_steps)}")
for u in unconverged_steps:
    s_idx = u['step_index']
    t0 = u['t_start_yr']
    t1 = u['t_end_yr']
    it = u['n_iter']
    r0 = u['init_picard_res']
    rf = u['final_picard_res']
    mr = u['step_mass_residual_kg']
    dr = u['step_diag_residual_kg']
    print(f"Step {s_idx} (t={t0:.2f}-{t1:.2f} yr): iters={it} | init_res={r0:.4e} | final_res={rf:.4e} | mass_res={mr:+.4e} kg | diag_res={dr:+.4e} kg")
    print(f"  Residual progression at iters [1, 10, 20, 30, 40, 50, 60, 70, 80]:")
    h = u['res_history']
    sample_pts = [0, 9, 19, 29, 39, 49, 59, 69, 79]
    print("  " + " -> ".join([f"i={i+1}:{h[i]:.2e}" for i in sample_pts if i < len(h)]))

