import sys
import os
sys.path.insert(0, os.path.abspath("antarctic-ice-volume-prediction"))

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from src.physics.ssa_2d.constants import SSA2DConstants, CONST_DEFAULT
from src.physics.ssa_2d.grid import Grid2D
from src.physics.ssa_2d.rheology import compute_effective_viscosity_2d
from src.physics.ssa_2d.friction import compute_flotation_fraction_and_surface, compute_basal_drag_coefficient
from src.physics.ssa_2d.boundary import compute_calving_front_traction

print("Imports succeeded!")
