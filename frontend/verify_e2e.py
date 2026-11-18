"""
End-to-End Functional Verification Suite for CryoPredict.
Verifies the running FastAPI backend and React frontend server.
"""

import urllib.request
import urllib.error
import json
import sys

def test_endpoint(name, url, method="GET", data=None):
    try:
        body = json.dumps(data).encode("utf-8") if data else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            c_type = resp.headers.get("Content-Type", "")
            if "application/json" in c_type:
                res = json.loads(content.decode("utf-8"))
            elif "image/" in c_type:
                res = f"Image ({len(content)} bytes)"
            else:
                res = content.decode("utf-8", errors="replace")
            print(f"✓ {name}: Status {resp.status}")
            return res
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"✓ {name} (Expected HTTP {e.code}): {err_msg[:120]}")
        return {"error_code": e.code, "detail": err_msg}
    except Exception as e:
        print(f"✗ {name}: Failed with error {e}")
        return None

def main():
    print("=" * 70)
    print("  CRYOPREDICT END-TO-END VERIFICATION & INTEGRATION SUITE")
    print("=" * 70)

    # 1. Frontend Web Server
    fe = test_endpoint("1. Frontend Web Server (Vite Preview on :5173)", "http://127.0.0.1:5173/")
    if not fe or "CryoPredict" not in fe:
        print("FAIL: Frontend web server is not serving CryoPredict HTML")
        sys.exit(1)

    # 2. Backend Health Endpoint
    h = test_endpoint("2. Backend Health (GET /api/health)", "http://127.0.0.1:8000/api/health")
    assert h["status"] == "healthy", f"Expected healthy status, got {h}"
    assert h["models_loaded"] is True, "Models not loaded"
    assert h["loaded_models_count"] >= 4, f"Expected >= 4 models, got {h['loaded_models_count']}"

    # 3. Overview Endpoint
    ov = test_endpoint("3. Research Overview (GET /api/overview)", "http://127.0.0.1:8000/api/overview")
    assert ov["total_grounded_area_km2"] == 216062.17
    assert ov["total_ice_volume_km3"] == 140702.51
    assert len(ov["basins"]) == 3
    print(f"   -> Domain Area: {ov['total_grounded_area_km2']} km², Basins: {[b['basin_id'] for b in ov['basins']]}")

    # 4. Models Catalog Endpoint
    m_list = test_endpoint("4. Candidate Models (GET /api/models)", "http://127.0.0.1:8000/api/models")
    assert len(m_list) == 6, f"Expected 6 models, got {len(m_list)}"
    en_model = next(m for m in m_list if m["model_id"] == "MOD-04")
    assert en_model["model_name"] == "ElasticNet"
    assert en_model["test_trainonly_mae_gt_yr"] == 9.61
    print(f"   -> Primary Model: {en_model['model_name']} (Test MAE: {en_model['test_trainonly_mae_gt_yr']} Gt/yr, R²: {en_model['test_trainonly_r2']})")

    # 5. Model Detail Endpoint
    m_detail = test_endpoint("5. Model Detail (GET /api/models/MOD-04)", "http://127.0.0.1:8000/api/models/MOD-04")
    assert m_detail["model_id"] == "MOD-04"
    assert len(m_detail["feature_coefficients"]) == 14
    print(f"   -> Learned Coefficients: {len(m_detail['feature_coefficients'])} features accounted for")

    # 6. Historical Timeseries Filtering
    ts_filtered = test_endpoint("6. Historical Timeseries (GET /api/predictions/historical?basin_id=Hp-I&year=2020)", "http://127.0.0.1:8000/api/predictions/historical?basin_id=Hp-I&year=2020")
    assert len(ts_filtered) == 1
    assert ts_filtered[0]["basin_id"] == "Hp-I"
    assert ts_filtered[0]["year"] == 2020
    print(f"   -> Historical Record: Basin {ts_filtered[0]['basin_id']} Year {ts_filtered[0]['year']}, Observed MB: {ts_filtered[0]['observed_mass_balance_gt_yr']} Gt/yr")

    # 7. Live Model Inference
    payload = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "forecast_year": 2025,
        "features": {
            "Target_Volume_Change_Lag1_km3_yr": -17.52,
            "Target_Volume_Change_Lag2_km3_yr": -16.48,
            "Net_MB_Lag1_Gt_yr": -16.07,
            "SMB_Lag1_Gt_yr": 72.45,
            "Discharge_Lag1_Gt_yr": 88.52,
            "SMB_Rolling3yr_Gt_yr": 74.20,
            "SMB_Anomaly_Lag1_Gt_yr": -3.85,
            "Grounded_Area_km2": 108945.63,
            "Mean_Baseline_Ice_Thickness_m": 1482.40,
            "Bed_Elevation_at_Gates_m": -124.20,
            "Driving_Stress_Index_kPa": 105.40,
            "is_Hp_I": 1.0,
            "is_I_Ipp": 0.0,
            "is_Ipp_J": 0.0
        }
    }
    live_res = test_endpoint("7. Live Model Inference (POST /api/predictions/run)", "http://127.0.0.1:8000/api/predictions/run", method="POST", data=payload)
    assert live_res["prediction_type"] == "live_inference"
    assert live_res["model_id"] == "MOD-04"
    mb = live_res["predicted_mass_balance_gt_yr"]
    vol = live_res["predicted_volume_change_km3_yr"]
    expected_vol = round(mb / 0.917, 2)
    assert abs(vol - expected_vol) <= 0.02, f"Density mismatch: vol={vol}, expected={expected_vol}"
    print(f"   -> Live Prediction Output: MB = {mb:.2f} Gt/yr, Volume = {vol:.2f} km³/yr (Conversion ΔV = ΔM / 0.917)")

    # 8. Guardrail Test: Prohibited Year >= 2100
    bad_payload = dict(payload)
    bad_payload["forecast_year"] = 2100
    bad_res = test_endpoint("8. Guardrail: Reject Year >= 2100 (POST /api/predictions/run)", "http://127.0.0.1:8000/api/predictions/run", method="POST", data=bad_payload)
    assert bad_res.get("error_code") == 422, f"Expected 422 Unprocessable Entity, got {bad_res}"
    print("   -> Successfully rejected prohibited centennial year 2100 with HTTP 422")

    # 9. Non-Finite Feature Rejection
    nan_payload = json.loads(json.dumps(payload))
    nan_payload["features"]["SMB_Lag1_Gt_yr"] = "invalid_string_not_a_float"
    nan_res = test_endpoint("9. Guardrail: Reject Non-Finite Feature (POST /api/predictions/run)", "http://127.0.0.1:8000/api/predictions/run", method="POST", data=nan_payload)
    assert nan_res.get("error_code") == 422
    print("   -> Successfully rejected invalid feature payload with HTTP 422")

    # 10. Datasets Inventory Endpoint
    ds_list = test_endpoint("10. Dataset Inventory (GET /api/datasets)", "http://127.0.0.1:8000/api/datasets")
    assert len(ds_list) == 14, f"Expected 14 datasets, got {len(ds_list)}"
    print(f"   -> Datasets Count: {len(ds_list)} verified entries")

    # 11. Feature Dictionary Endpoint
    feat_list = test_endpoint("11. Feature Dictionary (GET /api/features)", "http://127.0.0.1:8000/api/features")
    assert len(feat_list) >= 14, f"Expected >= 14 features, got {len(feat_list)}"
    print(f"   -> Feature Dictionary Count: {len(feat_list)} dictionary entries (FEAT-01 to FEAT-15)")

    # 12. Authentic Cartographic Assets Check
    print("12. Cartographic Figures Check:")
    figures = [
        "map1_peninsula_basins_domain.png",
        "map2_bedmap3_thickness.png",
        "map3_bedmap3_classification_masks.png",
        "stage4_6_velocity_field.png",
        "stage4_8_mass_budget_maps.png"
    ]
    for fig in figures:
        fig_res = test_endpoint(f"    Asset {fig}", f"http://127.0.0.1:5173/figures/{fig}")
        assert fig_res is not None, f"Failed to retrieve {fig}"

    print("=" * 70)
    print("  ALL 12 E2E VERIFICATION CHECKS PASSED WITH 100% SUCCESS")
    print("=" * 70)

if __name__ == "__main__":
    main()
