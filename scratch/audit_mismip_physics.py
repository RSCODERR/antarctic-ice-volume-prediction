import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

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
)

print("Auditing MISMIP+ constants...")
print(f"Current CONST_MISMIP.C_bed = {CONST_MISMIP.C_bed:.4e} Pa (m/s)^(-1/3)")
# Official Asay-Davis (2016) Table 1:
# beta_2 = 3.160e6 Pa m^(-1/3) s^(1/3) = 1.0e4 Pa m^(-1/3) a^(1/3)
correct_C_si = 3.160e6
ratio = CONST_MISMIP.C_bed / correct_C_si
print(f"Official Table 1 C_bed     = {correct_C_si:.4e} Pa (m/s)^(-1/3)")
print(f"Discrepancy ratio: {ratio:.1f}x TOO STIFF in current code!")

