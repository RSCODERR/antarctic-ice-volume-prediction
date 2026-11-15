"""
src/physics/smb.py
==================
SMBConverter — unit-safe surface mass balance conversion and staging.

SMB data from RACMO2 / CESM2 arrives in various units:
  - kg m⁻² yr⁻¹  (mass flux — most common)
  - m yr⁻¹ (ice equivalent)
  - mm w.e. yr⁻¹  (millimetres water equivalent)

The solver requires m s⁻¹ (ice-equivalent metres per second) for each cell.

This module performs the conversions explicitly, with unit labelling at every
step.  It does NOT load actual SMB data — that requires the raw atmospheric
forcing files not available in the sandbox.

For Stage 1 synthetic testing, uniform or sinusoidal SMB fields are provided.

Governance:
  - Analytical smoothing estimates must NOT be used as SMB forcing.
  - Stage 1 uses synthetic SMB only.
  - Real forcing will be loaded in Stage 2 after data acquisition.

Units:  output always m s⁻¹ (ice equivalent).
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

from .constants import CONST, PhysicsConstants


class SMBConverter:
    """
    Convert SMB from various source units to solver units (m s⁻¹ ice equiv.).

    Parameters
    ----------
    const : PhysicsConstants
    """

    def __init__(self, const: PhysicsConstants = CONST) -> None:
        self.const = const

    # ------------------------------------------------------------------
    # Unit conversions
    # ------------------------------------------------------------------

    def from_kg_m2_s(
        self, smb_kg_m2_s: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [kg m⁻² s⁻¹] to [m s⁻¹ ice equivalent].

        Steps:
          kg m⁻² s⁻¹  →  m s⁻¹  (divide by ρ_ice)

        [m s⁻¹] = [kg m⁻² s⁻¹] / ρ_ice [kg m⁻³]
        """
        smb = np.asarray(smb_kg_m2_s, dtype=np.float64)
        return smb / self.const.rho_ice

    def from_kg_m2_yr(
        self, smb_kg_m2_yr: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [kg m⁻² yr⁻¹] to [m s⁻¹ ice equivalent].

        Steps:
          1. kg m⁻² yr⁻¹  →  kg m⁻² s⁻¹  (divide by yr_to_s)
          2. kg m⁻² s⁻¹  →  m s⁻¹         (divide by ρ_ice)

        [m s⁻¹] = [kg m⁻² yr⁻¹] / (ρ_ice [kg m⁻³] · yr_to_s [s yr⁻¹])
        """
        smb = np.asarray(smb_kg_m2_yr, dtype=np.float64)
        return smb / (self.const.rho_ice * self.const.yr_to_s)

    def from_m_ice_yr(
        self, smb_m_ice_yr: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [m ice yr⁻¹] to [m s⁻¹ ice equivalent].

        [m s⁻¹] = [m yr⁻¹] / yr_to_s
        """
        smb = np.asarray(smb_m_ice_yr, dtype=np.float64)
        return smb / self.const.yr_to_s

    def from_mm_we_yr(
        self, smb_mm_we_yr: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [mm w.e. yr⁻¹] to [m s⁻¹ ice equivalent].

        Steps:
          1. mm w.e. yr⁻¹  →  kg m⁻² yr⁻¹  (multiply by ρ_fw / 1000)
             Actually: 1 mm w.e. = 1 kg m⁻² (since ρ_fw = 1000 kg m⁻³)
          2. kg m⁻² yr⁻¹  →  m s⁻¹ (via from_kg_m2_yr)

        Note: 1 mm w.e. = 1 kg m⁻² (ρ_fw = 1000 kg m⁻³ exactly).
        """
        smb_kg = np.asarray(smb_mm_we_yr, dtype=np.float64)  # 1 mm w.e. = 1 kg/m²
        return self.from_kg_m2_yr(smb_kg)

    def to_kg_m2_s(
        self, smb_m_s: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [m s⁻¹ ice equivalent] to [kg m⁻² s⁻¹].

        [kg m⁻² s⁻¹] = [m s⁻¹] · ρ_ice [kg m⁻³]
        """
        smb = np.asarray(smb_m_s, dtype=np.float64)
        return smb * self.const.rho_ice

    def to_kg_m2_yr(
        self, smb_m_s: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [m s⁻¹ ice equivalent] to [kg m⁻² yr⁻¹].

        [kg m⁻² yr⁻¹] = [m s⁻¹] · (ρ_ice [kg m⁻³] · yr_to_s [s yr⁻¹])
        """
        smb = np.asarray(smb_m_s, dtype=np.float64)
        return smb * (self.const.rho_ice * self.const.yr_to_s)

    def to_mm_we_yr(
        self, smb_m_s: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [m s⁻¹ ice equivalent] to [mm w.e. yr⁻¹].

        Since 1 mm w.e. = 1 kg m⁻²:
        [mm w.e. yr⁻¹] = [kg m⁻² yr⁻¹]
        """
        return self.to_kg_m2_yr(smb_m_s)

    def to_m_ice_yr(
        self, smb_m_s: NDArray[np.float64] | float
    ) -> NDArray[np.float64]:
        """
        Convert SMB from [m s⁻¹ ice equivalent] to [m ice yr⁻¹].

        [m ice yr⁻¹] = [m s⁻¹] · yr_to_s [s yr⁻¹]
        """
        smb = np.asarray(smb_m_s, dtype=np.float64)
        return smb * self.const.yr_to_s

    # ------------------------------------------------------------------
    # Volumetric source term
    # ------------------------------------------------------------------

    def cell_volume_source(
        self,
        smb_m_s: NDArray[np.float64],
        width: NDArray[np.float64],
        dx: float,
    ) -> NDArray[np.float64]:
        """
        Compute volumetric SMB source S_i [m³ s⁻¹] for each cell.

        S_i = ṁ_i · W_i · Δx

        Parameters
        ----------
        smb_m_s : ndarray [m s⁻¹], shape (N,)
            Ice-equivalent accumulation rate (positive = mass gain).
        width : ndarray [m], shape (N,)
        dx : float [m]

        Returns
        -------
        S : ndarray [m³ s⁻¹], shape (N,)
        """
        smb_m_s = np.asarray(smb_m_s, dtype=np.float64)
        width = np.asarray(width, dtype=np.float64)
        return smb_m_s * width * dx

    def total_smb_mass_flux(
        self,
        smb_m_s: NDArray[np.float64],
        width: NDArray[np.float64],
        dx: float,
        n_grounded: int | None = None,
    ) -> float:
        """
        Total grounded SMB mass flux  Ṁ_SMB [kg s⁻¹].

        Ṁ_SMB = ρ_i · Σ_i S_i  (over grounded cells)

        Parameters
        ----------
        smb_m_s : ndarray [m s⁻¹]
        width : ndarray [m]
        dx : float [m]
        n_grounded : int, optional
            Number of grounded cells to sum over.  Defaults to all.
        """
        S = self.cell_volume_source(smb_m_s, width, dx)
        ng = n_grounded if n_grounded is not None else len(S)
        return float(np.sum(S[:ng]) * self.const.rho_ice)

    # ------------------------------------------------------------------
    # Synthetic SMB fields for Stage 1 testing
    # ------------------------------------------------------------------

    @staticmethod
    def synthetic_uniform(
        N: int, rate_m_ice_yr: float = 0.5
    ) -> NDArray[np.float64]:
        """
        Uniform SMB field [m ice yr⁻¹].

        Parameters
        ----------
        N : int
            Number of cells.
        rate_m_ice_yr : float
            Accumulation rate [m yr⁻¹].  Positive = accumulation.
        """
        return np.full(N, rate_m_ice_yr, dtype=np.float64)

    @staticmethod
    def synthetic_ablation_zone(
        N: int,
        accumulation_m_yr: float = 1.0,
        ablation_m_yr: float = -2.0,
        ablation_fraction: float = 0.3,
    ) -> NDArray[np.float64]:
        """
        SMB with an ablation zone in the terminal fraction of the flowline.

        Parameters
        ----------
        N : int
        accumulation_m_yr : float
            Accumulation in the upper domain [m ice yr⁻¹].
        ablation_m_yr : float
            Net ablation in the lower domain [m ice yr⁻¹]. Must be negative.
        ablation_fraction : float
            Fraction of cells in the ablation zone (from downstream end).
        """
        smb = np.full(N, accumulation_m_yr, dtype=np.float64)
        n_abl = int(N * ablation_fraction)
        smb[N - n_abl:] = ablation_m_yr
        return smb

    def __repr__(self) -> str:
        return f"SMBConverter(rho_ice={self.const.rho_ice}, yr_to_s={self.const.yr_to_s:.4e})"

