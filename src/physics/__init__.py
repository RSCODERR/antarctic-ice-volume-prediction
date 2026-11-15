"""
src/physics/__init__.py
=======================
Physical solver package — Stage 1 (Pillar 1 backbone).

Authorised by Phase 5.2.2.7 Conditional Pass review (2026-11-09).
Governance restrictions remain in force:
  - Domain A is frozen: 866 358 cells, 216 062.17 km², 500 m grid.
  - No ISMIP6 calibration of physical parameters.
  - No ML coupling or future projections in this package.
  - Conservation tests must demonstrate conservation; it may not be assumed.
"""

from .constants import PhysicsConstants
from .domain import FlowlineDomain
from .rheology import GlensFlowLaw
from .ssa_solver import SSASolver
from .basal_drag import BasalDrag
from .lateral_drag import LateralDrag
from .grounding_line import SchoofGLFlux
from .continuity import FVContinuitySolver
from .smb import SMBConverter
from .state import IceState

__all__ = [
    "PhysicsConstants",
    "FlowlineDomain",
    "GlensFlowLaw",
    "SSASolver",
    "BasalDrag",
    "LateralDrag",
    "SchoofGLFlux",
    "FVContinuitySolver",
    "SMBConverter",
    "IceState",
]

