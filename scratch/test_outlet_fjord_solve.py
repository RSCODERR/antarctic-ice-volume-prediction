import netCDF4 as nc
import numpy as np
from scipy.ndimage import gaussian_filter1d

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx_grid = 500.0
dy_grid = -500.0

# True outlet-fjord waypoints
pts = [
    (-2457000.0, 1305000.0), # Divide peak (s = 2017 m)
    (-2466040.2, 1305701.1), # GATE_IPP_01 (Leonardo Outlet)
    (-2478000.0, 1308000.0)  # Fjord mouth calving front into Flanders Bay
]

N_raw = 50
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
    w_thick[w_mask == 1] = -1.0 # exclude rock walls
    w_thick[w_mask == 0] = -1.0 # exclude open ocean
    
    if np.all(w_thick < 0):
        # if all rock or ocean, take raw point
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
mask_raw = np.array([int(sub_mask[r, c]) for r, c in zip(rel_r, rel_c)])

peak_idx = int(np.argmax(surf_raw[:10]))
term_idx = int(np.argmin(surf_raw))
if term_idx <= peak_idx:
    term_idx = len(surf_raw) - 1

thick_cut = thick_raw[peak_idx:term_idx+1].copy()
bed_cut = bed_raw[peak_idx:term_idx+1].copy()
surf_cut = surf_raw[peak_idx:term_idx+1].copy()

sigma_cells = 3.0
bed_s = gaussian_filter1d(bed_cut, sigma=sigma_cells, mode='nearest')
thick_s = gaussian_filter1d(thick_cut, sigma=sigma_cells, mode='nearest')
thick_s = np.maximum(thick_s, 50.0)

print(f"Thalweg extracted: N={len(thick_s)}, Length={len(thick_s)*0.5:.1f} km")
print(f"Surface: start={surf_cut[0]:.1f}m, end={surf_cut[-1]:.1f}m, drop={surf_cut[0]-surf_cut[-1]:.1f}m")
print(f"Bed: min={bed_s.min():.1f}m, mean={bed_s.mean():.1f}m, at GL={bed_s[-1]:.1f}m")
print(f"Thickness: min={thick_s.min():.1f}m, mean={thick_s.mean():.1f}m, at GL={thick_s[-1]:.1f}m")

# Test SSA solve with corrected LateralDrag
import sys
sys.path.insert(0, 'src')
from physics.constants import CONST
from physics.domain import FlowlineDomain
from physics.ssa_solver import SSASolver

domain = FlowlineDomain(
    x_centres=np.arange(len(thick_s))*500.0 + 250.0,
    bed=bed_s,
    width=np.full(len(thick_s), 3800.0),
    H_init=thick_s,
    name="FL_IIPP_01_OUTLET_FJORD"
)
state = domain.initial_state()
ssa = SSASolver(CONST, tol=1e-4, max_iter=80)
diag = ssa.solve(state, u_upstream=0.0)

print(f"SSA solve: converged={diag.converged}, iters={diag.n_iter}, res={diag.residual:.2e}")
print(f"Simulated GL Velocity: {diag.u[state.gl_cell] * CONST.yr_to_s:.1f} m/yr")
print(f"Simulated Mean Velocity: {np.nanmean(diag.u[:state.n_grounded]) * CONST.yr_to_s:.1f} m/yr")
print(f"Observed GATE_IPP_01 Velocity: 210.0 m/yr")
print(f"Discrepancy Ratio: {(diag.u[state.gl_cell] * CONST.yr_to_s) / 210.0:.2f}x")

