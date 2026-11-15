"""
src/physics/ssa_2d
==================
2D Depth-Integrated Shallow Shelf Approximation (SSA) solver package.
"""

from .constants import (
    SSA2DConstants,
    CONST_DEFAULT,
    CONST_MISMIP,
    SEC_PER_YEAR_JULIAN,
    SEC_PER_YEAR_MISMIP,
)
from .grid import Grid2D, BCType
from .rheology import (
    compute_strain_rates_2d,
    compute_effective_strain_rate_sq,
    compute_effective_viscosity_2d,
)
from .friction import (
    compute_flotation_fraction_and_surface,
    compute_basal_drag_coefficient,
)
from .boundary import compute_calving_front_traction
from .assembly import assemble_ssa_system_2d
from .solver import SSASolver2D, SSAResult2D, NonlinearConvergenceError
from .continuity import (
    step_continuity_2d,
    compute_cfl_timestep_2d,
    ContinuityResult2D,
)
from .mismip_plus import (
    create_mismip_bed,
    compute_mismip_melt_rate,
    find_grounding_line_x,
    compute_vaf_km3,
    create_mismip_initial_profile,
    MISMIPResult,
)

__all__ = [
    "SSA2DConstants",
    "CONST_DEFAULT",
    "CONST_MISMIP",
    "SEC_PER_YEAR_JULIAN",
    "SEC_PER_YEAR_MISMIP",
    "Grid2D",
    "BCType",
    "compute_strain_rates_2d",
    "compute_effective_strain_rate_sq",
    "compute_effective_viscosity_2d",
    "compute_flotation_fraction_and_surface",
    "compute_basal_drag_coefficient",
    "compute_calving_front_traction",
    "assemble_ssa_system_2d",
    "SSASolver2D",
    "SSAResult2D",
    "NonlinearConvergenceError",
    "step_continuity_2d",
    "compute_cfl_timestep_2d",
    "ContinuityResult2D",
    "create_mismip_bed",
    "compute_mismip_melt_rate",
    "find_grounding_line_x",
    "compute_vaf_km3",
    "create_mismip_initial_profile",
    "MISMIPResult",
]
