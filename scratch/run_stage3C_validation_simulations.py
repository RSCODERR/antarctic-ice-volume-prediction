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

configs = {
    'FL_HPI_02': {
        'name': 'Millett / Dyer Glacier System',
        'basin': 'Hp-I',
        'waypoints': [
            (-1837096.5, 856652.2),
            (-1831415.5, 815398.7),
            (-1820054.5, 742750.5)
        ],
        'width_m': 15200.0,
        'n_pts': 110,
        'obs_u_gl': 290.0,
        'obs_sigma': 18.03,
        'smb_yr': 0.45,
        'gate_id': 'GATE_HP_02'
    },
    'FL_IPPJ_03': {
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
    },
    'FL_IPPJ_01': {
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
}

cb_frozen = 8.168e+06 # Stage 3B.1 frozen parameter
dt = 0.02 * CONST.yr_to_s
n_steps = 250 # 5 years

validation_results = {}

for fl_id, cfg in configs.items():
    print(f"\n=======================================================")
    print(f"Processing Validation Target: {fl_id} ({cfg['name']})")
    print(f"=======================================================")
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
        name=fl_id,
        source=f'BedMachine_V4.1_Aligned_{fl_id}_Thalweg'
    )
    state = domain.initial_state()

    # Diagnostic SSA solve at t=0
    basal = BasalDrag(CONST, C_bed=cb_frozen)
    ssa = SSASolver(CONST, basal=basal, tol=1e-4, max_iter=80)
    diag_0 = ssa.solve(state, u_upstream=0.0)

    u_yr_0 = diag_0.u * CONST.yr_to_s
    u_gl_0 = u_yr_0[state.gl_cell]
    resid_0 = u_gl_0 - cfg['obs_u_gl']
    pct_0 = (resid_0 / cfg['obs_u_gl']) * 100.0
    z_0 = resid_0 / cfg['obs_sigma']

    print(f"Static Solve: u_gl={u_gl_0:.2f} m/yr | obs={cfg['obs_u_gl']:.2f} m/yr | diff={resid_0:+.2f} m/yr ({pct_0:+.1f}%, z={z_0:+.2f}s) | iters={diag_0.n_iter} | conv={diag_0.converged}")

    # Prognostic 5-year simulation
    smb_conv = SMBConverter(CONST)
    fv = FVContinuitySolver(CONST, ssa=ssa, smb_conv=smb_conv, use_schoof=False)
    smb_m_s = smb_conv.from_m_ice_yr(np.full(domain.N, cfg['smb_yr']))

    cur_state = state
    tot_smb = 0.0
    tot_outflow = 0.0
    tot_boundary = 0.0
    m_start = cur_state.compute_grounded_mass_kg()
    non_conv_steps = 0
    max_picard_res = 0.0

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for step in range(n_steps):
            cur_state, diag_step = fv.step(cur_state, smb_m_s=smb_m_s, dt=dt, u_upstream=0.0)
            tot_smb += diag_step.Mdot_SMB * dt
            tot_outflow += diag_step.Q_GL * CONST.rho_ice * dt
            tot_boundary += diag_step.dM_boundary
            max_picard_res = max(max_picard_res, diag_step.ssa_picard_residual)
            if not diag_step.ssa_converged:
                non_conv_steps += 1

    m_end = cur_state.compute_grounded_mass_kg()
    delta_m = m_end - m_start
    net_budget = tot_smb - tot_outflow + tot_boundary
    cum_res = delta_m - net_budget
    rel_mass_err = abs(cum_res) / m_start

    print(f"Prognostic 5-Yr Mass Balance:")
    print(f"  M_start: {m_start/1e12:.3f} Gt, M_end: {m_end/1e12:.3f} Gt, Delta M: {delta_m/1e12:.3f} Gt")
    print(f"  SMB: {tot_smb/1e12:+.3f} Gt, Outflow: {tot_outflow/1e12:+.3f} Gt, Boundary: {tot_boundary/1e12:+.3f} Gt")
    print(f"  Discrete Mass Residual: {cum_res:+.4e} kg (Relative error: {rel_mass_err:.2e})")
    print(f"  Picard Convergence: {n_steps - non_conv_steps}/{n_steps} steps converged ({non_conv_steps} reached 80 iters, max_res={max_picard_res:.4e})")

    validation_results[fl_id] = {
        'fl_id': fl_id,
        'name': cfg['name'],
        'basin': cfg['basin'],
        'gate_id': cfg['gate_id'],
        'N_cells': domain.N,
        'N_grounded': state.n_grounded,
        'gl_cell': state.gl_cell,
        'u_sim_gl': u_gl_0,
        'u_obs_gl': cfg['obs_u_gl'],
        'sigma_obs': cfg['obs_sigma'],
        'abs_resid': resid_0,
        'pct_error': pct_0,
        'z_score': z_0,
        'within_uncert': abs(resid_0) <= cfg['obs_sigma'],
        'diag_iters': diag_0.n_iter,
        'diag_res': diag_0.residual,
        'diag_conv': diag_0.converged,
        'm_start_kg': m_start,
        'm_end_kg': m_end,
        'delta_m_kg': delta_m,
        'tot_smb_kg': tot_smb,
        'tot_outflow_kg': tot_outflow,
        'tot_boundary_kg': tot_boundary,
        'mass_resid_kg': cum_res,
        'rel_mass_err': rel_mass_err,
        'prog_non_conv_steps': non_conv_steps,
        'prog_max_picard_res': max_picard_res,
        'u_profile_yr': u_yr_0,
        'H_profile': state.H,
        'bed_profile': state.bed,
        'surf_profile': state.H + state.bed,
        'x_km': state.x_centres / 1000.0
    }

print("\nAll 3 validation simulations completed.")
