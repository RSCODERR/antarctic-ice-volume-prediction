"""
src/physics/constants.py
========================
Frozen physical constants for the Antarctic Peninsula 1D SSA solver.

All values are traceable to published sources.  No value here is calibrated
against ISMIP6 or against future-projection targets.

Units:   SI throughout  (m, kg, s, Pa = kg m⁻¹ s⁻²).
"""

from __future__ import annotations
import dataclasses


@dataclasses.dataclass(frozen=True)
class PhysicsConstants:
    """
    Immutable container for physical constants used throughout Stage 1.

    Attributes are grouped by category and each carries a unit tag and source.
    Creating a second instance with different values is allowed for sensitivity
    experiments, but the defaults must not be changed without reviewer sign-off.
    """

    # ------------------------------------------------------------------
    # Ice rheology  (Glen's flow law, n = 3)
    # ------------------------------------------------------------------
    glen_n: float = 3.0
    """Glen's flow-law exponent [-].  Paterson (1994); Cuffey & Paterson (2010)."""

    A_cold: float = 3.5e-25
    """Glen rate factor A for cold ice [Pa⁻³ s⁻¹].
    Valid below ~263 K.  Cuffey & Paterson (2010) Table 3.4."""

    A_temperate: float = 2.4e-24
    """Glen rate factor A for temperate ice [Pa⁻³ s⁻¹].
    Valid above ~263 K.  Cuffey & Paterson (2010) Table 3.4."""

    # Default A used in solver — cold Antarctic Peninsula interior.
    A_default: float = 3.5e-25
    """Default Glen rate factor A [Pa⁻³ s⁻¹].  Conservative cold-ice value."""

    eps_reg_viscosity: float = 1.0e-15
    """Strain-rate regularisation [s⁻¹].  Prevents singular viscosity at ice
    divides where du/dx → 0.  See Phase 5.2.1 audit."""

    # Derived: B = A^(-1/n)  — computed at runtime, not stored here.

    # ------------------------------------------------------------------
    # Basal sliding  (Weertman sliding law)
    # ------------------------------------------------------------------
    weertman_m: float = 1.0 / 3.0
    """Weertman sliding exponent m = 1/3  [-].  Paterson (1994)."""

    C_bed: float = 1.0e7
    """Basal drag coefficient  [Pa (m s⁻¹)⁻^(1/3)].
    C_bed in τ_b = C_bed |u|^(m-1) u.  Phase 5.2.1 audit value.
    NOT calibrated against ISMIP6."""

    u_reg: float = 3.17e-12
    """Basal-drag regularisation velocity [m s⁻¹].
    Equivalent to 1×10⁻⁴ m yr⁻¹.  Phase 5.2.1 audit.
    Prevents division by zero in u^(m-1) at u → 0."""

    # ------------------------------------------------------------------
    # Ice density and seawater
    # ------------------------------------------------------------------
    rho_ice: float = 917.0
    """Ice density [kg m⁻³].  Cuffey & Paterson (2010)."""

    rho_water: float = 1028.0
    """Seawater density [kg m⁻³].  Standard oceanographic value."""

    rho_freshwater: float = 1000.0
    """Freshwater density [kg m⁻³].  Used for SLR conversion only."""

    # ------------------------------------------------------------------
    # Gravity
    # ------------------------------------------------------------------
    g: float = 9.81
    """Gravitational acceleration [m s⁻²]."""

    # ------------------------------------------------------------------
    # Schoof grounding-line flux
    # ------------------------------------------------------------------
    C_schoof: float = 0.61
    """Dimensionless prefactor in Schoof (2007) Eq. 29 GL flux formula [-].
    Value from Schoof (2007) for n=3, m=1/3.  NOT calibrated against ISMIP6."""

    # ------------------------------------------------------------------
    # Domain (frozen — Phase 2.6 audit)
    # ------------------------------------------------------------------
    domain_dx: float = 500.0
    """Grid spacing [m].  FROZEN — Phase 2.6 baseline."""

    domain_n_cells: int = 866_358
    """Total grounded cells in Domain A [-].  FROZEN — Phase 2.6 baseline."""

    domain_area_km2: float = 216_062.17
    """Grounded Domain A area [km²].  FROZEN — Phase 2.6 baseline."""

    # ------------------------------------------------------------------
    # Numerical defaults
    # ------------------------------------------------------------------
    picard_max_iter: int = 25
    """Maximum Picard iterations per timestep [-].  Engineering limit."""

    picard_tol: float = 1.0e-5
    """Picard convergence tolerance [-].  Empirical engineering criterion."""

    u_scale: float = 10.0 / (365.25 * 24 * 3600)
    """Velocity scale for mixed Picard residual [m s⁻¹].
    Corresponds to 10 m yr⁻¹.  Prevents zero-division at ice divide."""

    picard_omega_default: float = 0.5
    """Default under-relaxation parameter ω ∈ [0.4, 0.6] [-].
    Engineering estimate; Stage 1 calibration may refine within range."""

    dt_target: float = 0.05 * 365.25 * 24 * 3600
    """Target timestep [s].  Corresponds to 0.05 yr ≈ 18.25 days."""

    # ------------------------------------------------------------------
    # Unit-conversion helpers (read-only computed at class level)
    # ------------------------------------------------------------------
    yr_to_s: float = 365.25 * 24.0 * 3600.0
    """Seconds per year [s yr⁻¹]."""

    s_to_yr: float = 1.0 / (365.25 * 24.0 * 3600.0)
    """Years per second [yr s⁻¹]."""

    Gt_to_kg: float = 1.0e12
    """Gigatonnes to kilograms [kg Gt⁻¹]."""

    kg_to_Gt: float = 1.0e-12
    """Kilograms to gigatonnes [Gt kg⁻¹]."""

    # ------------------------------------------------------------------
    # Lateral drag
    # ------------------------------------------------------------------
    lateral_shape_factor: float = 5.0
    """Lateral drag shape factor.  Derivation: τ_wall = (5 ū / (A W))^(1/n).
    The factor 5 arises from the parabolic velocity profile assumption.
    Phase 5.2.2.5 confirmed: no factor of 2 in denominator."""

    def B(self, A: float | None = None) -> float:
        """Glen stiffness B = A^(-1/n)  [Pa s^(1/n)]."""
        a = A if A is not None else self.A_default
        return a ** (-1.0 / self.glen_n)

    def flotation_thickness(self, z_sl: float, z_bed: float) -> float:
        """
        Minimum ice thickness for grounding at sea level z_sl over bed z_bed.

        H_crit = (ρ_w / ρ_i) · max(0, z_sl − z_bed)   [m]

        Returns 0 for bedrock above sea level (land-terminating case).
        """
        return (self.rho_water / self.rho_ice) * max(0.0, z_sl - z_bed)

    def __repr__(self) -> str:
        return (
            f"PhysicsConstants("
            f"n={self.glen_n}, A={self.A_default:.2e}, "
            f"rho_i={self.rho_ice}, rho_w={self.rho_water}, "
            f"dx={self.domain_dx} m)"
        )


# Module-level singleton — import and use directly in most modules.
CONST = PhysicsConstants()

