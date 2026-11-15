"""
src/physics/ssa_2d/constants.py
===============================
Physical and numerical constants for the 2D Shallow Shelf Approximation (SSA) solver.

Strict SI units throughout:
  - Length: metres [m]
  - Time: seconds [s] (conversions to years [a or yr] provided explicitly)
  - Mass: kilograms [kg]
  - Stress / Pressure: Pascals [Pa = N m⁻² = kg m⁻¹ s⁻²]
  - Viscosity: [Pa s = kg m⁻¹ s⁻¹]
  - Velocity: [m s⁻¹]
  - Strain rate: [s⁻¹]
  - Traction coefficient: [Pa (m s⁻¹)⁻ᵐ]
"""

from __future__ import annotations
import dataclasses

# Standard astronomical / glaciological year lengths
SEC_PER_YEAR_JULIAN: float = 31556926.0   # 365.2422 days
SEC_PER_YEAR_MISMIP: float = 31536000.0   # 365.0 days (Cornford et al. 2020 / Asay-Davis et al. 2016)


@dataclasses.dataclass(frozen=True)
class SSA2DConstants:
    """
    Physical and numerical constants container for 2D SSA.
    """
    # Density and gravity
    rho_ice: float = 917.0          # Ice density [kg m⁻³] (BedMachine default)
    rho_water: float = 1028.0       # Seawater density [kg m⁻³]
    g: float = 9.81                 # Gravitational acceleration [m s⁻²]

    # Glen's flow law rheology (n = 3)
    glen_n: float = 3.0             # Flow law exponent [-]
    glen_A: float = 3.5e-25         # Rate factor [Pa⁻³ s⁻¹] (cold ice)
    eps_0: float = 1.0e-10          # Strain-rate regularisation [s⁻¹]

    # Basal friction (Weertman sliding law: tau_b = - C_bed |u|^(m-1) u)
    weertman_m: float = 1.0 / 3.0   # Sliding law exponent m = 1/3 [-]
    C_bed: float = 1.0e7            # Basal drag coefficient [Pa (m s⁻¹)⁻ᵐ]
    u_0: float = 3.17e-12           # Basal velocity regularisation [m s⁻¹] (~1e-4 m yr⁻¹)

    # Calving and flotation
    flotation_margin: float = 0.0   # Height above flotation threshold [m]

    # Numerical solver settings
    picard_omega: float = 0.6       # Under-relaxation parameter omega in [0.3, 0.8]
    picard_max_iter: int = 100      # Maximum Picard iterations
    tol_rel_residual: float = 1e-5  # Relative L2 residual tolerance ||R|| / ||R_0||
    tol_vel_step: float = 3.17e-9   # Max velocity update norm ||Delta u||_inf [m s⁻¹] (~0.1 m yr⁻¹)

    # Time conversion factor for this constant set
    sec_per_year: float = SEC_PER_YEAR_JULIAN

    @classmethod
    def mismip_plus(cls) -> SSA2DConstants:
        """
        Factory method returning official MISMIP+ benchmark constants
        (Asay-Davis et al. 2016; Cornford et al. 2020).
        """
        spy = SEC_PER_YEAR_MISMIP
        # MISMIP+ Glen A = 2.0e-17 Pa⁻³ a⁻¹
        A_mismip = 2.0e-17 / spy
        # MISMIP+ Table 1: beta_2 = 1.0e4 Pa (m a⁻¹)⁻(1/3) = 3.160e6 Pa (m s⁻¹)⁻(1/3)
        C_bed_mismip_si = 1.0e4 * (spy ** (1.0 / 3.0))  # ~3.15938e6 Pa (m s⁻¹)⁻(1/3)

        return cls(
            rho_ice=918.0,
            rho_water=1028.0,
            g=9.8,
            glen_n=3.0,
            glen_A=A_mismip,
            eps_0=1.0e-10,
            weertman_m=1.0 / 3.0,
            C_bed=C_bed_mismip_si,
            u_0=1.0e-4 / spy,
            flotation_margin=0.0,
            picard_omega=0.5,
            picard_max_iter=150,
            tol_rel_residual=1e-5,
            tol_vel_step=0.1 / spy,
            sec_per_year=spy,
        )


CONST_DEFAULT = SSA2DConstants()
CONST_MISMIP = SSA2DConstants.mismip_plus()

