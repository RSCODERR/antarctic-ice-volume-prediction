import sys
import os
sys.path.insert(0, os.path.abspath("."))

import time
import numpy as np

from src.physics.ssa_2d.constants import SSA2DConstants, CONST_MISMIP
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface
from src.physics.ssa_2d.solver import SSASolver2D
from src.physics.ssa_2d.continuity import step_continuity_2d
from src.physics.ssa_2d.mismip_plus import (
    create_mismip_bed,
    compute_mismip_melt_rate,
    find_grounding_line_x,
    compute_vaf_km3,
    create_mismip_initial_profile,
)

print("Testing MISMIP+ fast test...")
grid = Grid2D(
    Lx=640_000.0, Ly=80_000.0, Nx=64, Ny=9,
    bc_west="no_slip", bc_east="calving_front", bc_south="free_slip", bc_north="free_slip"
)
bed = create_mismip_bed(grid)
const = CONST_MISMIP
spy = const.sec_per_year

H_init = create_mismip_initial_profile(grid, bed, const, x_gl_target=450_000.0)
f_gr, s, _ = compute_flotation_fraction_and_surface(H_init, bed, const)
x_gl_init = find_grounding_line_x(f_gr, grid)
vaf_init = compute_vaf_km3(H_init, bed, grid, const)

print(f"Initial state: x_GL = {x_gl_init/1000.0:.2f} km, VAF = {vaf_init:.1f} km3")

