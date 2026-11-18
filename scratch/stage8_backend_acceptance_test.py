"""
Stage 8.0 Comprehensive Backend Acceptance Test
Exhaustively audits all endpoints, query parameters, input validation,
error contracts, security hygiene, and scientific calculations.
"""

import sys
import os
from pathlib import Path

# Add backend and backend/tests directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
tests_dir = backend_dir / "tests"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(tests_dir))

from conftest import TestApiClient
from app.config import settings

def run_backend_acceptance():
    print("=" * 80)
    print("STAGE 8.0 — BACKEND ACCEPTANCE AUDIT")
    print("=" * 80)

    client = TestApiClient()
    results = {}
    failures = []

    def check(test_name: str, condition: bool, msg: str = ""):
        if condition:
            print(f"  [PASS] {test_name}")
            results[test_name] = "PASS"
        else:
            print(f"  [FAIL] {test_name}: {msg}")
            results[test_name] = f"FAIL: {msg}"
            failures.append(f"{test_name}: {msg}")

    # 1. Root Endpoint
    print("\n--- 1. Root Endpoint (GET /) ---")
    r = client.get("/")
    check("Root 200 OK", r.status_code == 200)
    data = r.json()
    check("Root platform identity", data.get("platform") == settings.APP_NAME)
    check("Root documentation links", "documentation" in data and "health" in data)
    check("Root scientific notice present", "historical" in data.get("scientific_notice", "").lower())

    # 2. Health Endpoint
    print("\n--- 2. Health Endpoint (GET /api/health) ---")
    r = client.get("/api/health")
    check("Health 200 OK", r.status_code == 200)
    data = r.json()
    check("Health status healthy", data.get("status") in ("healthy", "degraded"))
    check("Models loaded flag", data.get("models_loaded") is True)
    check("Loaded models count >= 4", data.get("loaded_models_count", 0) >= 4)
    check("Primary model ready", data.get("primary_model_status") == "READY")

    # 3. Overview Endpoint
    print("\n--- 3. Overview Endpoint (GET /api/overview) ---")
    r = client.get("/api/overview")
    check("Overview 200 OK", r.status_code == 200)
    data = r.json()
    check("Overview has total grounded area", data.get("total_grounded_area_km2") == 216062.17)
    check("Overview has total ice volume", data.get("total_ice_volume_km3") == 140702.51)
    check("Overview has basin summary", len(data.get("basins", [])) == 3)
    check("Overview has scientific disclosures", len(data.get("scientific_disclosures", [])) >= 2)

    # 4. Models Endpoints
    print("\n--- 4. Models Endpoints (GET /api/models, /comparison, /{id}) ---")
    r = client.get("/api/models")
    check("List models 200 OK", r.status_code == 200)
    models = r.json()
    check("All 6 candidate models listed", len(models) == 6)
    model_ids = [m["model_id"] for m in models]
    check("Model IDs MOD-01 to MOD-06", set(model_ids) == {f"MOD-0{i}" for i in range(1, 7)})

    # Comparison endpoint
    r_comp = client.get("/api/models/comparison")
    check("Model comparison 200 OK", r_comp.status_code == 200)
    check("Model comparison non-empty", len(r_comp.json()) >= 6)

    # Individual model details
    for m_id in ["MOD-01", "MOD-02", "MOD-03", "MOD-04", "MOD-05", "MOD-06"]:
        r_det = client.get(f"/api/models/{m_id}")
        check(f"Detail for {m_id} 200 OK", r_det.status_code == 200)
        d = r_det.json()
        check(f"Detail {m_id} has model_id", d.get("model_id") == m_id)
        check(f"Detail {m_id} has basin performance", len(d.get("basin_performance", {})) >= 3)

    # Detail 404
    r_bad_id = client.get("/api/models/MOD-999")
    check("Model detail 404 on invalid ID", r_bad_id.status_code == 404)
    check("Model detail clean 404 message", "not found" in r_bad_id.json()["detail"].lower())

    # 5. Datasets Endpoint
    print("\n--- 5. Datasets Endpoint (GET /api/datasets) ---")
    r = client.get("/api/datasets")
    check("Datasets 200 OK", r.status_code == 200)
    datasets = r.json()
    check("At least 5 datasets returned", len(datasets) >= 5)
    ds_names = [d["dataset_name"] for d in datasets]
    check("IMBIE dataset present", any("IMBIE" in n for n in ds_names))

    # 6. Features Endpoint
    print("\n--- 6. Features Endpoint (GET /api/features) ---")
    r = client.get("/api/features")
    check("Features 200 OK", r.status_code == 200)
    feats = r.json()
    check("At least 14 frozen features returned", len(feats) >= 14)
    check("All features have name and category", all(f.get("feature_name") and f.get("feature_category") for f in feats))

    # 7. Historical Predictions
    print("\n--- 7. Historical Predictions (GET /api/predictions/historical) ---")
    r_all = client.get("/api/predictions/historical")
    check("Historical all 200 OK", r_all.status_code == 200)
    hist_all = r_all.json()
    check("Total 138 historical records (46 years x 3 basins)", len(hist_all) == 138)

    # Filter by basin
    for b in ["Hp-I", "I-Ipp", "Ipp-J"]:
        r_b = client.get(f"/api/predictions/historical?basin_id={b}")
        check(f"Filter basin {b} 200 OK", r_b.status_code == 200)
        check(f"Basin {b} count == 46", len(r_b.json()) == 46)

    # Filter by year
    r_y = client.get("/api/predictions/historical?year=2015")
    check("Filter year 2015 200 OK", r_y.status_code == 200)
    check("Year 2015 count == 3", len(r_y.json()) == 3)

    # Invalid basin 400
    r_bad_b = client.get("/api/predictions/historical?basin_id=BadBasin")
    check("Invalid basin returns 400", r_bad_b.status_code == 400)

    # 8. Historical Features Endpoint (Mode A)
    print("\n--- 8. Historical Antecedent Features (GET /api/predictions/historical/features) ---")
    r_hf = client.get("/api/predictions/historical/features?basin_id=Hp-I&year=2015")
    check("Historical features 200 OK", r_hf.status_code == 200)
    hf_data = r_hf.json()
    check("Historical features count == 14", len(hf_data["features"]) == 14)
    check("Historical features temporal explanation present", "temporal_explanation" in hf_data)

    # Test antecedent ordering: Year t uses lag_1 from t-1, lag_2 from t-2
    # Check that year 2015 differs from year 2016
    r_hf_2016 = client.get("/api/predictions/historical/features?basin_id=Hp-I&year=2016")
    check("Historical features 2016 200 OK", r_hf_2016.status_code == 200)
    check(
        "Antecedent values differ between 2015 and 2016",
        hf_data["features"]["Net_MB_Lag1_Gt_yr"] != r_hf_2016.json()["features"]["Net_MB_Lag1_Gt_yr"]
    )

    # Test out of bounds year returns 404
    r_oob_low = client.get("/api/predictions/historical/features?basin_id=Hp-I&year=1950")
    check("Year 1950 out-of-bounds 404", r_oob_low.status_code == 404)
    r_oob_high = client.get("/api/predictions/historical/features?basin_id=Hp-I&year=2050")
    check("Year 2050 out-of-bounds 404", r_oob_high.status_code == 404)

    # 9. Live Inference (POST /api/predictions/run)
    print("\n--- 9. Live Inference (POST /api/predictions/run) ---")
    test_features = {
        "Target_Volume_Change_Lag1_km3_yr": -42.42,
        "Target_Volume_Change_Lag2_km3_yr": -4.09,
        "Net_MB_Lag1_Gt_yr": -3.76,
        "SMB_Lag1_Gt_yr": 67.24,
        "Discharge_Lag1_Gt_yr": 71.00,
        "SMB_Rolling3yr_Gt_yr": 68.50,
        "SMB_Anomaly_Lag1_Gt_yr": -1.26,
        "Grounded_Area_km2": 108945.63,
        "Mean_Baseline_Ice_Thickness_m": 1482.40,
        "Bed_Elevation_at_Gates_m": -124.20,
        "Driving_Stress_Index_kPa": 105.40,
        "is_Hp_I": 1.0,
        "is_I_Ipp": 0.0,
        "is_Ipp_J": 0.0
    }

    # Test all supported models
    for m in ["MOD-01", "MOD-02", "MOD-03", "MOD-04", "MOD-05", "MOD-06"]:
        req_payload = {
            "basin_id": "Hp-I",
            "model_id": m,
            "features": test_features
        }
        r_infer = client.post("/api/predictions/run", json=req_payload)
        check(f"Inference with {m} 200 OK", r_infer.status_code == 200)
        resp_data = r_infer.json()
        check(f"Inference {m} returns predicted_mass_balance_gt_yr", "predicted_mass_balance_gt_yr" in resp_data)
        check(f"Inference {m} returns predicted_volume_change_km3_yr", "predicted_volume_change_km3_yr" in resp_data)

    # Prohibited year >= 2100 rejected with 422
    req_2100 = {
        "basin_id": "Hp-I",
        "model_id": "MOD-04",
        "features": test_features,
        "forecast_year": 2100
    }
    r_2100 = client.post("/api/predictions/run", json=req_2100)
    check("Prohibited year 2100 rejected with 422", r_2100.status_code == 422)
    check("Error mentions Centennial projections", "Centennial projections" in str(r_2100.json()))

    # Invalid basin rejected with 422
    req_bad_basin = {
        "basin_id": "UnknownBasin",
        "model_id": "MOD-04",
        "features": test_features
    }
    r_bad_basin = client.post("/api/predictions/run", json=req_bad_basin)
    check("Invalid basin rejected with 422", r_bad_basin.status_code == 422)

    # Invalid model rejected with 400
    req_bad_model = {
        "basin_id": "Hp-I",
        "model_id": "MOD-99",
        "features": test_features
    }
    r_bad_model = client.post("/api/predictions/run", json=req_bad_model)
    check("Invalid model rejected with 400", r_bad_model.status_code == 400)

    # Missing feature rejected with 422
    incomplete_features = {k: v for k, v in test_features.items() if k != "Target_Volume_Change_Lag1_km3_yr"}
    req_missing = {
        "basin_id": "Hp-I",
        "model_id": "MOD-04",
        "features": incomplete_features
    }
    r_missing = client.post("/api/predictions/run", json=req_missing)
    check("Missing feature rejected with 422", r_missing.status_code == 422)

    # 10. Future Projections: Scenarios (GET /api/projections/scenarios)
    print("\n--- 10. Future Projections: Scenarios (GET /api/projections/scenarios) ---")
    r_scen = client.get("/api/projections/scenarios")
    check("Projections scenarios 200 OK", r_scen.status_code == 200)
    scenarios = r_scen.json()
    check("Exactly 3 scenarios returned", len(scenarios) == 3)
    scen_map = {s["id"]: s for s in scenarios}
    check("RCP8.5 has NATIVE_ISMIP6 watermark", scen_map["RCP8.5"]["scenario_watermark"] == "NATIVE_ISMIP6")
    check("RCP2.6 has NATIVE_ISMIP6 watermark", scen_map["RCP2.6"]["scenario_watermark"] == "NATIVE_ISMIP6")
    check("SSP2-4.5 has SCALED_EMULATOR_SYNTHESIS watermark", scen_map["SSP2-4.5"]["scenario_watermark"] == "SCALED_EMULATOR_SYNTHESIS")
    check("SSP2-4.5 scaling alpha == 0.35", scen_map["SSP2-4.5"]["scaling_coefficient_alpha"] == 0.35)

    # 11. Future Projections: Models (GET /api/projections/models)
    print("\n--- 11. Future Projections: Models (GET /api/projections/models) ---")
    r_fmodels = client.get("/api/projections/models")
    check("Projections models 200 OK", r_fmodels.status_code == 200)
    fmodel_data = r_fmodels.json()
    check("Target variable is Delta_VAF_Climate_km3", fmodel_data["target_variable"] == "Delta_VAF_Climate_km3")
    check("Quantiles evaluated == [0.10, 0.16, 0.50, 0.84, 0.90]", fmodel_data["quantiles_evaluated"] == [0.10, 0.16, 0.50, 0.84, 0.90])
    check("LOMFO folds == 10", len(fmodel_data["lomfo_folds"]) == 10)
    check("Candidate comparisons == 4", len(fmodel_data["candidate_comparisons"]) == 4)
    check("Scientific notices present", len(fmodel_data["scientific_notices"]) >= 5)

    # 12. Future Projections: Availability (GET /api/projections/availability)
    print("\n--- 12. Future Projections: Availability (GET /api/projections/availability) ---")
    r_avail = client.get("/api/projections/availability")
    check("Projections availability 200 OK", r_avail.status_code == 200)
    avail_data = r_avail.json()
    check("Start year == 2015", avail_data["start_year"] == 2015)
    check("End year == 2100", avail_data["end_year"] == 2100)
    check("Total years == 86", avail_data["total_years"] == 86)
    check("Total records == 1,032", avail_data["total_records"] == 1032)
    spatial_dict = {s["id"]: s["name"] for s in avail_data["spatial_units"]}
    check("Hp-I is Palmer Land West", spatial_dict.get("Hp-I") == "Palmer Land West")
    check("I-Ipp is Graham Land", spatial_dict.get("I-Ipp") == "Graham Land")
    check("Ipp-J is Palmer Land East", spatial_dict.get("Ipp-J") == "Palmer Land East")
    check("Domain_A is Entire Antarctic Peninsula (Domain A)", spatial_dict.get("Domain_A") == "Entire Antarctic Peninsula (Domain A)")

    # 13. Future Projections: Trajectory Combinations (GET /api/projections/trajectory)
    print("\n--- 13. Future Projections: Trajectory Combinations ---")
    spatial_units = ["Domain_A", "Hp-I", "I-Ipp", "Ipp-J"]
    scenarios_list = ["RCP8.5", "RCP2.6", "SSP2-4.5"]

    all_combos_tested = 0
    all_points_monotonic = True
    all_sle_monotonic = True

    for sp in spatial_units:
        for sc in scenarios_list:
            r_t = client.get(f"/api/projections/trajectory?scenario={sc}&spatial_unit={sp}")
            check(f"Trajectory {sc} / {sp} 200 OK", r_t.status_code == 200)
            t_data = r_t.json()
            check(f"Trajectory {sc} / {sp} point_count == 86", t_data["point_count"] == 86)

            # Check watermark
            expected_wm = "SCALED_EMULATOR_SYNTHESIS" if sc == "SSP2-4.5" else "NATIVE_ISMIP6"
            check(f"Trajectory {sc} / {sp} watermark == {expected_wm}", t_data["scenario_watermark"] == expected_wm)

            # Check 2050 and 2100 summary
            check(f"Trajectory {sc} / {sp} has summary_2050", t_data["summary_2050"] is not None)
            check(f"Trajectory {sc} / {sp} has summary_2100", t_data["summary_2100"] is not None)

            # Check quantile monotonicity across all 86 points
            for pt in t_data["trajectory"]:
                v10, v16, v50, v84, v90 = (
                    pt["delta_vaf_10th_km3"],
                    pt["delta_vaf_16th_km3"],
                    pt["delta_vaf_median_km3"],
                    pt["delta_vaf_84th_km3"],
                    pt["delta_vaf_90th_km3"]
                )
                if not (v10 <= v16 + 1e-4 and v16 <= v50 + 1e-4 and v50 <= v84 + 1e-4 and v84 <= v90 + 1e-4):
                    all_points_monotonic = False

                s10, s16, s50, s84, s90 = (
                    pt["delta_sle_10th_mm"],
                    pt["delta_sle_16th_mm"],
                    pt["delta_sle_median_mm"],
                    pt["delta_sle_84th_mm"],
                    pt["delta_sle_90th_mm"]
                )
                if not (s10 <= s16 + 1e-4 and s16 <= s50 + 1e-4 and s50 <= s84 + 1e-4 and s84 <= s90 + 1e-4):
                    all_sle_monotonic = False

            all_combos_tested += 1

    check(f"All 12 spatial/scenario combos verified ({all_combos_tested}/12)", all_combos_tested == 12)
    check("All 1,032 records have monotonic VAF quantiles", all_points_monotonic)
    check("All 1,032 records have monotonic SLE quantiles", all_sle_monotonic)

    # Test year filtering
    r_filt = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=Hp-I&start_year=2040&end_year=2080")
    check("Trajectory year range filtering 200 OK", r_filt.status_code == 200)
    check("Filtered point count == 41 (2040-2080)", r_filt.json()["point_count"] == 41)

    # Test invalid trajectory requests
    r_bad_scen = client.get("/api/projections/trajectory?scenario=RCP9.9&spatial_unit=Hp-I")
    check("Invalid scenario rejected with 400", r_bad_scen.status_code == 400)

    r_bad_unit = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=NonExistent")
    check("Invalid spatial unit rejected with 400", r_bad_unit.status_code == 400)

    r_bad_years = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=Hp-I&start_year=2090&end_year=2020")
    check("Inverted year range rejected with 400", r_bad_years.status_code == 400)

    # 14. Security & Error Safety Audit
    print("\n--- 14. Security & Path Leakage Audit ---")
    error_endpoints = [
        client.get("/api/models/INVALID_MODEL_NAME_XYZ"),
        client.get("/api/predictions/historical?basin_id=INVALID_BASIN"),
        client.get("/api/predictions/historical/features?basin_id=Hp-I&year=9999"),
        client.post("/api/predictions/run", json={"basin_id": "Bad", "model_id": "bad", "target_year": 2015, "features": {}}),
        client.get("/api/projections/trajectory?scenario=BAD_SCENARIO&spatial_unit=Hp-I")
    ]

    clean_errors = True
    for resp in error_endpoints:
        text = str(resp.json())
        if "C:\\" in text or "/Users/" in text or "Traceback" in text:
            clean_errors = False
            print(f"  [SECURITY LEAK DETECTED]: {text}")

    check("No absolute filesystem paths or tracebacks in error responses", clean_errors)

    # Summary
    print("\n" + "=" * 80)
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v == "PASS")
    print(f"TOTAL CHECKS: {total_checks} | PASSED: {passed_checks} | FAILED: {len(failures)}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  - {f}")
    else:
        print("ALL BACKEND ACCEPTANCE CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

    return len(failures) == 0

if __name__ == "__main__":
    success = run_backend_acceptance()
    sys.exit(0 if success else 1)
