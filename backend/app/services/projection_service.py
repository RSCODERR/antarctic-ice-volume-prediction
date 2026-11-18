"""
Projection service for CryoPredict future projections (Stage 7.1/7.2).
Loads and queries the verified Stage 7.1 future projection manifest,
model metadata, and LOMFO validation tables.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any

from app.config import settings
from app.schemas.projection import (
    ScenarioItem,
    CandidateModelComparison,
    LOMFOFoldResult,
    FutureModelInfoResponse,
    SpatialUnitInfo,
    AvailabilityResponse,
    TrajectoryPoint,
    ProjectionTrajectoryResponse
)

logger = logging.getLogger("cryopredict.projection_service")

class ProjectionService:
    def __init__(self):
        self.is_loaded = False
        self.df_projections: Optional[pd.DataFrame] = None
        self.metadata: Optional[Dict[str, Any]] = None
        self.df_comparison: Optional[pd.DataFrame] = None
        self.df_lomfo: Optional[pd.DataFrame] = None

    def load_data(self):
        """Load future projection CSV, metadata, and validation tables into memory."""
        try:
            # Use rearranged manifest if available (Stage 7.3), otherwise fall back to Stage 7.1
            rearr_path = getattr(settings, "PATH_PROJECTIONS_REARRANGED_FILE", settings.PATH_PROJECTIONS_DIR / "stage7_3_future_projections_rearranged_2015_2100.csv")
            orig_path = getattr(settings, "PATH_PROJECTIONS_ORIGINAL_FILE", settings.PATH_PROJECTIONS_DIR / "stage7_1_future_projections_2015_2100.csv")
            
            proj_path = rearr_path if rearr_path.exists() else orig_path
            meta_path = settings.PATH_FUTURE_MODELS_DIR / "future_model_metadata.json"
            comp_path = settings.PATH_TABLES / "stage7_1_model_comparison.csv"
            lomfo_path = settings.PATH_TABLES / "stage7_1_lomfo_validation.csv"

            logger.info(f"Loading projection manifest from: {proj_path}")
            if not proj_path.exists():
                raise FileNotFoundError(f"Projection manifest not found at {proj_path}")
            self.df_projections = pd.read_csv(proj_path)

            if meta_path.exists():
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
            else:
                logger.warning(f"Metadata file not found at {meta_path}")
                self.metadata = {}

            if comp_path.exists():
                self.df_comparison = pd.read_csv(comp_path)
            else:
                logger.warning(f"Model comparison table not found at {comp_path}")
                self.df_comparison = pd.DataFrame()

            if lomfo_path.exists():
                self.df_lomfo = pd.read_csv(lomfo_path)
            else:
                logger.warning(f"LOMFO table not found at {lomfo_path}")
                self.df_lomfo = pd.DataFrame()

            self.is_loaded = True
            logger.info(f"Loaded {len(self.df_projections)} future projection records.")
        except Exception as e:
            logger.error(f"Failed to load projection data: {e}", exc_info=True)
            raise

    def get_scenarios(self) -> List[ScenarioItem]:
        """Return actual supported scenarios and their provenance."""
        if not self.is_loaded:
            self.load_data()

        scenarios = [
            ScenarioItem(
                id="RCP8.5",
                name="RCP 8.5 (High Emissions)",
                scenario_type="NATIVE_ISMIP6",
                scenario_watermark="NATIVE_ISMIP6",
                tier="Tier-1",
                scaling_coefficient_alpha=None,
                description="High radiative forcing pathway reaching +8.5 W/m² by 2100. Primary ISMIP6 multi-model experiment.",
                provenance_note="Directly simulated across 16 ice-sheet model configurations driven by NorESM1-M, MIROC-ESM-CHEM, and CCSM4 in the Seroussi et al. (2020) archive."
            ),
            ScenarioItem(
                id="RCP2.6",
                name="RCP 2.6 (Aggressive Mitigation)",
                scenario_type="NATIVE_ISMIP6",
                scenario_watermark="NATIVE_ISMIP6",
                tier="Tier-2",
                scaling_coefficient_alpha=None,
                description="Aggressive greenhouse gas mitigation pathway stabilizing below +2.6 W/m² by 2100. Native ISMIP6 Tier-2 experiment.",
                provenance_note="Directly simulated across ISMIP6 models driven by NorESM1-M and CCSM4."
            ),
            ScenarioItem(
                id="SSP2-4.5",
                name="SSP2-4.5 (Scaled Synthesis)",
                scenario_type="SCALED_EMULATOR_SYNTHESIS",
                scenario_watermark="SCALED_EMULATOR_SYNTHESIS",
                tier="Derived",
                scaling_coefficient_alpha=0.35,
                description="Intermediate stabilization pathway synthesized via cumulative radiative forcing pattern scaling (alpha=0.35). Not native to ISMIP6.",
                provenance_note="Synthesized via cumulative radiative pattern scaling between RCP2.6 and RCP8.5 baselines: Radiative forcing is parameterized at ~4.5 W/m²; this scenario was NOT directly executed in the ISMIP6 Seroussi et al. protocol."
            )
        ]
        return scenarios

    def get_model_info(self) -> FutureModelInfoResponse:
        """Return QGB model metadata, candidate comparisons, and LOMFO validation results."""
        if not self.is_loaded:
            self.load_data()

        comparisons = []
        if self.df_comparison is not None and not self.df_comparison.empty:
            for _, r in self.df_comparison.iterrows():
                comparisons.append(
                    CandidateModelComparison(
                        candidate_model_name=str(r["Candidate_Model_Name"]),
                        model_type=str(r["Model_Type"]),
                        oof_rmse_km3=float(r["Out_of_Family_RMSE_km3"]),
                        oof_mae_km3=float(r["Out_of_Family_MAE_km3"]),
                        oof_bias_km3=float(r["Out_of_Family_Bias_km3"]),
                        oof_r2=float(r["Out_of_Family_R2"]),
                        mae_2050_km3=float(r["MAE_at_2050_km3"]),
                        mae_2100_km3=float(r["MAE_at_2100_km3"]),
                        supports_non_gaussian_quantiles=bool(r["Supports_Non_Gaussian_Quantiles"]),
                        recommendation=str(r["Validation_Recommendation"])
                    )
                )

        lomfo_folds = []
        if self.df_lomfo is not None and not self.df_lomfo.empty:
            for _, r in self.df_lomfo.iterrows():
                lomfo_folds.append(
                    LOMFOFoldResult(
                        fold_index=int(r["Fold_Index"]),
                        held_out_family=str(r["Held_Out_Family"]),
                        member_models_count=int(r["Member_Models_Count"]),
                        member_models_list=str(r["Member_Models_List"]),
                        test_records_count=int(r["Test_Records_Count"]),
                        rmse_km3=float(r["QGB_Median_RMSE_km3"]),
                        mae_km3=float(r["QGB_Median_MAE_km3"]),
                        bias_km3=float(r["QGB_Median_Bias_km3"]),
                        r2=float(r["QGB_Median_R2"]),
                        empirical_coverage_68pct=float(r["Empirical_Coverage_68Pct"]),
                        mean_interval_width_km3=float(r["Mean_Prediction_Interval_Width_km3"]),
                        mae_2050_km3=float(r["MAE_2050_km3"]),
                        mae_2100_km3=float(r["MAE_2100_km3"]),
                        validation_gate_status=str(r["Validation_Gate_Status"])
                    )
                )

        notices = [
            "Future outputs represent Volume Above Flotation (ΔVAF) and derived Sea-Level Equivalent (SLE), not total grounded solid-ice volume.",
            "The nominal 68% prediction interval previously achieved 62.6% empirical out-of-family coverage across held-out model families.",
            "The QGB emulator is a research projection emulator and has conditional, not definitive, validation.",
            "The physical SSA solver is a historical transient model and is not an independently validated 2100 forecasting engine.",
            "SSP2-4.5 is a scaled emulator synthesis (alpha=0.35), not a native ISMIP6 scenario.",
            "Monotone quantile rearrangement (Chernozhukov et al., 2010) guarantees monotonic ordering (q10 <= q16 <= q50 <= q84 <= q90) without altering the uncalibrated nature of empirical prediction bounds."
        ]

        return FutureModelInfoResponse(
            model_id="STAGE7_1_QGB_ENSEMBLE",
            model_name="Multi-Model Quantile Gradient Boosting Projection Emulator",
            model_class="Quantile Gradient Boosted Regression Trees (Scikit-Learn GradientBoostingRegressor)",
            target_variable="Delta_VAF_Climate_km3",
            density_constant_gt_km3=0.917,
            gmsl_conversion_gt_mm=361.8,
            quantiles_evaluated=[0.10, 0.16, 0.50, 0.84, 0.90],
            features=self.metadata.get("feature_names", []),
            supported_scenarios=["RCP8.5", "RCP2.6", "SSP2-4.5 (Synthesized)"],
            supported_basins=["Hp-I", "I-Ipp", "Ipp-J", "Domain_A"],
            validation_protocol="Leave-One-Model-Family-Out (LOMFO, 10 Folds)",
            overall_metrics={
                "oof_r2": float(self.metadata.get("oof_overall_r2", 0.4843)),
                "oof_rmse_km3": float(self.metadata.get("oof_overall_rmse_km3", 567.18)),
                "oof_mae_km3": float(self.metadata.get("oof_overall_mae_km3", 256.85)),
                "oof_bias_km3": -12.70,
                "nominal_coverage_pct": 68.0,
                "empirical_coverage_pct": 62.6,
                "mean_interval_width_km3": 492.32,
                "mae_at_2050_km3": 182.49,
                "mae_at_2100_km3": 542.15
            },
            candidate_comparisons=comparisons,
            lomfo_folds=lomfo_folds,
            scientific_notices=notices
        )

    def get_availability(self) -> AvailabilityResponse:
        """Return available years, spatial units, and scenario combinations from manifest."""
        if not self.is_loaded:
            self.load_data()

        spatial_units = [
            SpatialUnitInfo(
                id="Hp-I",
                name="Palmer Land West",
                type="IMBIE_Basin",
                sector_id=16,
                description="Western Palmer Land & English Coast (Sector 16 / Bellingshausen Sea slopes)."
            ),
            SpatialUnitInfo(
                id="I-Ipp",
                name="Graham Land",
                type="IMBIE_Basin",
                sector_id=17,
                description="Northern Antarctic Peninsula / Graham Land (Sector 17 / Danco & Graham Coasts)."
            ),
            SpatialUnitInfo(
                id="Ipp-J",
                name="Palmer Land East",
                type="IMBIE_Basin",
                sector_id=18,
                description="Eastern Palmer Land & Larsen Coast (Sector 18 / Weddell Sea / Larsen C grounding zones)."
            ),
            SpatialUnitInfo(
                id="Domain_A",
                name="Entire Antarctic Peninsula (Domain A)",
                type="Aggregate_Domain",
                sector_id=None,
                description="Aggregate Region 3 covering all three IMBIE basins (Hp-I + I-Ipp + Ipp-J)."
            )
        ]

        scenarios = ["RCP8.5", "RCP2.6", "SSP2-4.5"]
        metrics = ["Delta_VAF_km3", "Delta_SLE_mm"]

        return AvailabilityResponse(
            start_year=int(self.df_projections["Year"].min()),
            end_year=int(self.df_projections["Year"].max()),
            total_years=int(self.df_projections["Year"].nunique()),
            spatial_units=spatial_units,
            scenarios=scenarios,
            metrics=metrics,
            total_records=len(self.df_projections)
        )

    def get_trajectory(
        self,
        scenario: str,
        spatial_unit: str,
        start_year: Optional[int] = 2015,
        end_year: Optional[int] = 2100
    ) -> ProjectionTrajectoryResponse:
        """Retrieve precomputed multi-quantile future trajectory for a scenario and spatial unit."""
        if not self.is_loaded:
            self.load_data()

        # Normalize scenario
        scen_norm = scenario.strip().upper()
        scen_map = {
            "RCP8.5": "RCP8.5",
            "RCP85": "RCP8.5",
            "RCP 8.5": "RCP8.5",
            "RCP2.6": "RCP2.6",
            "RCP26": "RCP2.6",
            "RCP 2.6": "RCP2.6",
            "SSP2-4.5": "SSP2-4.5",
            "SSP245": "SSP2-4.5",
            "SSP 2-4.5": "SSP2-4.5"
        }
        if scen_norm not in scen_map:
            raise ValueError(f"Invalid scenario '{scenario}'. Supported: 'RCP8.5', 'RCP2.6', 'SSP2-4.5'.")
        canonical_scen = scen_map[scen_norm]

        # Normalize spatial unit
        spat_norm = spatial_unit.strip()
        spat_map = {
            "Hp-I": "Hp-I",
            "hp-i": "Hp-I",
            "HP-I": "Hp-I",
            "I-Ipp": "I-Ipp",
            "i-ipp": "I-Ipp",
            "I-IPP": "I-Ipp",
            "Ipp-J": "Ipp-J",
            "ipp-j": "Ipp-J",
            "IPP-J": "Ipp-J",
            "Domain_A": "Domain_A",
            "domain_a": "Domain_A",
            "DOMAIN_A": "Domain_A",
            "Domain A": "Domain_A",
            "Region 3": "Domain_A",
            "region 3": "Domain_A"
        }
        if spat_norm not in spat_map:
            raise ValueError(f"Invalid spatial unit '{spatial_unit}'. Supported: 'Hp-I', 'I-Ipp', 'Ipp-J', 'Domain_A'.")
        canonical_basin = spat_map[spat_norm]

        # Filter manifest
        df = self.df_projections[
            (self.df_projections["Scenario"] == canonical_scen) &
            (self.df_projections["Basin_ID"] == canonical_basin)
        ]

        if df.empty:
            raise ValueError(f"No trajectory found for scenario '{canonical_scen}' and basin '{canonical_basin}'.")

        s_year = start_year if start_year is not None else 2015
        e_year = end_year if end_year is not None else 2100

        df_filtered = df[(df["Year"] >= s_year) & (df["Year"] <= e_year)].sort_values("Year")

        scenario_type = df_filtered["Scenario_Type"].iloc[0] if not df_filtered.empty else (
            "SCALED_EMULATOR_SYNTHESIS" if canonical_scen == "SSP2-4.5" else "NATIVE_ISMIP6"
        )
        watermark = scenario_type

        basin_names = {
            "Hp-I": "Palmer Land West (Sector 16)",
            "I-Ipp": "Graham Land (Sector 17)",
            "Ipp-J": "Palmer Land East (Sector 18)",
            "Domain_A": "Entire Antarctic Peninsula (Domain A / Region 3)"
        }

        rho_i = 0.917
        A_ocean = 361.8

        points: List[TrajectoryPoint] = []
        for _, row in df_filtered.iterrows():
            y = int(row["Year"])
            v_med = float(row["Delta_VAF_Median_km3"])
            v_16 = float(row["Delta_VAF_16th_km3"])
            v_84 = float(row["Delta_VAF_84th_km3"])
            v_10 = float(row["Delta_VAF_10th_km3"])
            v_90 = float(row["Delta_VAF_90th_km3"])

            # Manifest has Delta_SLE_Median_mm, Delta_SLE_16th_mm, Delta_SLE_84th_mm, and Stage 7.3 rearranged 10th/90th
            sle_med = float(row["Delta_SLE_Median_mm"])
            sle_16 = float(row["Delta_SLE_16th_mm"])
            sle_84 = float(row["Delta_SLE_84th_mm"])
            # Derive or read 10th and 90th SLE:
            # 10th percentile SLE corresponds to 90th percentile VAF:
            sle_10 = float(row["Delta_SLE_10th_mm"]) if "Delta_SLE_10th_mm" in row and not pd.isna(row["Delta_SLE_10th_mm"]) else round(- (v_90 * rho_i) / A_ocean, 3)
            # 90th percentile SLE corresponds to 10th percentile VAF:
            sle_90 = float(row["Delta_SLE_90th_mm"]) if "Delta_SLE_90th_mm" in row and not pd.isna(row["Delta_SLE_90th_mm"]) else round(- (v_10 * rho_i) / A_ocean, 3)

            points.append(
                TrajectoryPoint(
                    year=y,
                    delta_vaf_median_km3=v_med,
                    delta_vaf_16th_km3=v_16,
                    delta_vaf_84th_km3=v_84,
                    delta_vaf_10th_km3=v_10,
                    delta_vaf_90th_km3=v_90,
                    delta_sle_median_mm=sle_med,
                    delta_sle_16th_mm=sle_16,
                    delta_sle_84th_mm=sle_84,
                    delta_sle_10th_mm=sle_10,
                    delta_sle_90th_mm=sle_90
                )
            )

        # Compute summary points at 2050 and 2100 if present
        def get_summary_dict(yr: int):
            row_yr = df[df["Year"] == yr]
            if not row_yr.empty:
                r = row_yr.iloc[0]
                v_10 = float(r["Delta_VAF_10th_km3"])
                v_90 = float(r["Delta_VAF_90th_km3"])
                s_10 = float(r["Delta_SLE_10th_mm"]) if "Delta_SLE_10th_mm" in r and not pd.isna(r["Delta_SLE_10th_mm"]) else round(- (v_90 * rho_i) / A_ocean, 3)
                s_90 = float(r["Delta_SLE_90th_mm"]) if "Delta_SLE_90th_mm" in r and not pd.isna(r["Delta_SLE_90th_mm"]) else round(- (v_10 * rho_i) / A_ocean, 3)
                return {
                    "year": yr,
                    "delta_vaf_16th_km3": float(r["Delta_VAF_16th_km3"]),
                    "delta_vaf_median_km3": float(r["Delta_VAF_Median_km3"]),
                    "delta_vaf_84th_km3": float(r["Delta_VAF_84th_km3"]),
                    "delta_vaf_10th_km3": v_10,
                    "delta_vaf_90th_km3": v_90,
                    "sle_16th_mm": float(r["Delta_SLE_16th_mm"]),
                    "sle_median_mm": float(r["Delta_SLE_Median_mm"]),
                    "sle_84th_mm": float(r["Delta_SLE_84th_mm"]),
                    "sle_10th_mm": s_10,
                    "sle_90th_mm": s_90,
                    "scenario_watermark": watermark,
                    "validation_status": "CONDITIONAL_PASS"
                }
            return None

        return ProjectionTrajectoryResponse(
            scenario=canonical_scen,
            scenario_type=scenario_type,
            scenario_watermark=watermark,
            spatial_unit=canonical_basin,
            spatial_unit_name=basin_names.get(canonical_basin, canonical_basin),
            start_year=s_year,
            end_year=e_year,
            point_count=len(points),
            target_variable="Delta_VAF_Climate_km3",
            target_disclaimer=(
                "These projections represent changes in Volume Above Flotation (ΔVAF) "
                "and derived Sea-Level Equivalent (SLE). They do not represent total grounded solid-ice volume."
            ),
            sle_formula="SLE (mm) = - (Delta_VAF (km³) * 0.917) / 361.8",
            summary_2050=get_summary_dict(2050),
            summary_2100=get_summary_dict(2100),
            trajectory=points
        )

# Global singleton
projection_service = ProjectionService()
