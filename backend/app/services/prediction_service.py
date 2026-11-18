"""
Prediction Service orchestrating live inference execution, validation, and response packaging.
"""

import uuid
from datetime import datetime, timezone
import logging
from typing import Dict, Any

from app.schemas.prediction import InferenceRequest, InferenceResponse
from app.services.model_service import model_service
from app.config import settings

logger = logging.getLogger(__name__)

class PredictionService:
    """Orchestrates interactive prediction requests with scientific validation."""

    def __init__(self):
        self.model_svc = model_service

    def run_inference(self, req: InferenceRequest) -> InferenceResponse:
        """
        Executes live inference with strict input checks and glaciological safeguards.
        """
        # 1. Scientific Safeguard Check: Centennial Projections
        if req.forecast_year is not None and req.forecast_year >= 2100:
            raise ValueError(
                "Prohibited forecast horizon: year >= 2100 requested. "
                "CryoPredict models are strictly 1-year ahead autoregressive historical predictors. "
                "Century-scale forecasting without coupled physical climate forcing is scientifically invalid."
            )

        # 2. Basin dummy consistency validation
        feat_dict = req.features.model_dump()
        basin = req.basin_id
        
        # Verify that the basin dummy matches the requested basin_id
        if basin == "Hp-I" and (feat_dict.get("is_Hp_I") != 1.0 or feat_dict.get("is_I_Ipp") != 0.0 or feat_dict.get("is_Ipp_J") != 0.0):
            logger.warning("Basin dummy mismatch detected. Aligning basin fixed-effect indicators to 'Hp-I'.")
            feat_dict["is_Hp_I"] = 1.0
            feat_dict["is_I_Ipp"] = 0.0
            feat_dict["is_Ipp_J"] = 0.0
        elif basin == "I-Ipp" and (feat_dict.get("is_I_Ipp") != 1.0 or feat_dict.get("is_Hp_I") != 0.0 or feat_dict.get("is_Ipp_J") != 0.0):
            logger.warning("Basin dummy mismatch detected. Aligning basin fixed-effect indicators to 'I-Ipp'.")
            feat_dict["is_Hp_I"] = 0.0
            feat_dict["is_I_Ipp"] = 1.0
            feat_dict["is_Ipp_J"] = 0.0
        elif basin == "Ipp-J" and (feat_dict.get("is_Ipp_J") != 1.0 or feat_dict.get("is_Hp_I") != 0.0 or feat_dict.get("is_I_Ipp") != 0.0):
            logger.warning("Basin dummy mismatch detected. Aligning basin fixed-effect indicators to 'Ipp-J'.")
            feat_dict["is_Hp_I"] = 0.0
            feat_dict["is_I_Ipp"] = 0.0
            feat_dict["is_Ipp_J"] = 1.0

        # 3. Model Execution
        pred_mb, pred_vol, uncert_std, m_id, m_name = self.model_svc.predict(
            model_identifier=req.model_id,
            basin_id=basin,
            features_dict=feat_dict
        )

        basin_names = {
            "Hp-I": "Palmer Land West",
            "I-Ipp": "Graham Land",
            "Ipp-J": "Palmer Land East"
        }
        b_name = basin_names.get(basin, basin)

        # Compute volume uncertainty if mass uncertainty is available
        uncert_vol = (uncert_std / settings.SOLID_ICE_DENSITY_GT_KM3) if uncert_std is not None else None
        effective_year = req.target_year if req.target_year is not None else req.forecast_year

        # 4. Package Response
        return InferenceResponse(
            prediction_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_id=m_id,
            model_name=m_name,
            model_class="Regularized Supervised Benchmark" if "MOD-04" in m_id else "Benchmarked Candidate",
            basin_id=basin,
            basin_name=b_name,
            target_year=effective_year,
            forecast_year=effective_year,
            inference_mode=req.inference_mode,
            input_features=feat_dict,
            predicted_mass_balance_gt_yr=round(pred_mb, 2),
            predicted_volume_change_km3_yr=round(pred_vol, 2),
            density_conversion_used="Delta V = Delta M / 0.917 Gt/km3 (Solid ice density: 917 kg/m3)",
            uncertainty_std_gt_yr=round(uncert_std, 2) if uncert_std is not None else None,
            uncertainty_std_km3_yr=round(uncert_vol, 2) if uncert_vol is not None else None,
            prediction_type="live_inference",
            scientific_disclosure=(
                "Historical basin-level annual prediction regularized on 1979-2024 observations. "
                "Calendar year is NOT an input feature to the model; predictions are governed strictly by the 14 physical predictors. "
                "This is NOT a validated 2100 climate projection and must not be used for multi-decadal sea-level forecasting."
            )
        )

prediction_service = PredictionService()
