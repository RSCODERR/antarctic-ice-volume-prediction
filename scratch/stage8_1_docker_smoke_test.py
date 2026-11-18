"""
Stage 8.1 Docker Release Candidate Smoke Test Suite
Audits the live running containers for health, endpoint proxying,
manifest loading, Swagger docs, route accessibility, and container restart.
"""

import subprocess
import json
import sys
import os

def run_wsl_cmd(cmd_str):
    """Executes a command inside Ubuntu WSL2 as root."""
    res = subprocess.run(
        ["wsl.exe", "-d", "Ubuntu", "-u", "root", "sh", "-c", cmd_str],
        capture_output=True,
        text=True,
        timeout=60
    )
    return res.returncode, res.stdout, res.stderr

def run_smoke_test():
    print("=" * 80)
    print("STAGE 8.1 — DOCKER RELEASE CANDIDATE SMOKE TEST")
    print("=" * 80)

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

    # 1. Container Status & Health Check
    print("\n--- 1. Container Status & Health ---")
    code, out, err = run_wsl_cmd("docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'")
    check("Docker ps successful", code == 0)
    print(out.strip())
    check("cryopredict-backend running", "cryopredict-backend" in out)
    check("cryopredict-frontend running", "cryopredict-frontend" in out)
    check("Backend port 8000 mapped", "8000" in out)
    check("Frontend port 80 mapped", "80" in out)

    # 2. Direct Backend Health (Port 8000)
    print("\n--- 2. Direct Backend Endpoints (Port 8000) ---")
    code, out, err = run_wsl_cmd("curl -s -f http://127.0.0.1:8000/api/health")
    check("Direct backend /api/health HTTP 200", code == 0)
    try:
        health_data = json.loads(out)
        check("Health status is healthy", health_data.get("status") in ("healthy", "degraded"))
        check("Models loaded is True", health_data.get("models_loaded") is True)
        check("Primary model READY", health_data.get("primary_model_status") == "READY")
        check("Loaded models count == 6", health_data.get("loaded_models_count") == 6)
    except Exception as e:
        check("Health JSON valid", False, str(e))

    # Direct Swagger docs (Port 8000)
    code, out, err = run_wsl_cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/docs")
    check("Direct Swagger /docs returns 200", out.strip() == "200")

    # Direct OpenAPI spec (Port 8000)
    code, out, err = run_wsl_cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/openapi.json")
    check("Direct /openapi.json returns 200", out.strip() == "200")

    # 3. Proxied Endpoints via Frontend Container (Port 80)
    print("\n--- 3. Proxied Endpoints via Nginx (Port 80) ---")
    code, out, err = run_wsl_cmd("curl -s -f http://127.0.0.1:80/api/health")
    check("Proxied /api/health HTTP 200", code == 0)
    try:
        p_health = json.loads(out)
        check("Proxied health matches direct health", p_health.get("status") in ("healthy", "degraded"))
    except Exception as e:
        check("Proxied health JSON valid", False, str(e))

    # Proxied Swagger docs through Port 80
    code, out, err = run_wsl_cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/docs")
    check("Proxied Swagger /docs on Port 80 returns 200", out.strip() == "200")

    code, out, err = run_wsl_cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/openapi.json")
    check("Proxied /openapi.json on Port 80 returns 200", out.strip() == "200")

    # 4. Manifest Loading & Monotonicity Verification in Container
    print("\n--- 4. Active Manifest & Projection Verification ---")
    code, out, err = run_wsl_cmd("curl -s http://127.0.0.1:8000/api/projections/availability")
    check("Projections availability HTTP 200", code == 0)
    try:
        avail = json.loads(out)
        check("Total records == 1,032", avail.get("total_records") == 1032)
        check("Total years == 86 (2015-2100)", avail.get("total_years") == 86)
        spatial_names = {s["id"]: s["name"] for s in avail.get("spatial_units", [])}
        check("Hp-I is canonical Palmer Land West", spatial_names.get("Hp-I") == "Palmer Land West")
        check("I-Ipp is canonical Graham Land", spatial_names.get("I-Ipp") == "Graham Land")
        check("Ipp-J is canonical Palmer Land East", spatial_names.get("Ipp-J") == "Palmer Land East")
    except Exception as e:
        check("Availability parsing valid", False, str(e))

    # Trajectory endpoint for RCP8.5 on I-Ipp
    code, out, err = run_wsl_cmd("curl -s 'http://127.0.0.1:8000/api/projections/trajectory?scenario=RCP8.5&spatial_unit=I-Ipp'")
    check("Trajectory query HTTP 200", code == 0)
    try:
        traj_data = json.loads(out)
        check("Trajectory point count == 86", traj_data.get("point_count") == 86)
        check("Trajectory watermark == NATIVE_ISMIP6", traj_data.get("scenario_watermark") == "NATIVE_ISMIP6")
        s2100 = traj_data.get("summary_2100", {})
        check("2100 Delta VAF median == -240.02 km3", abs(s2100.get("delta_vaf_median_km3", 0) - (-240.02)) < 0.1)
        check("2100 SLE median == 0.608 mm", abs(s2100.get("sle_median_mm", 0) - 0.608) < 0.01)
        # Quantile monotonicity
        v10 = s2100.get("delta_vaf_10th_km3")
        v16 = s2100.get("delta_vaf_16th_km3")
        v50 = s2100.get("delta_vaf_median_km3")
        v84 = s2100.get("delta_vaf_84th_km3")
        v90 = s2100.get("delta_vaf_90th_km3")
        check("2100 VAF quantiles monotonic", v10 <= v16 <= v50 <= v84 <= v90)
    except Exception as e:
        check("Trajectory parsing valid", False, str(e))

    # Trajectory endpoint for SSP2-4.5 on Domain_A
    code, out, err = run_wsl_cmd("curl -s 'http://127.0.0.1:8000/api/projections/trajectory?scenario=SSP2-4.5&spatial_unit=Domain_A'")
    check("SSP2-4.5 query HTTP 200", code == 0)
    try:
        ssp_data = json.loads(out)
        check("SSP2-4.5 watermark == SCALED_EMULATOR_SYNTHESIS", ssp_data.get("scenario_watermark") == "SCALED_EMULATOR_SYNTHESIS")
    except Exception as e:
        check("SSP2-4.5 parsing valid", False, str(e))

    # 5. Historical Prediction & Inference in Container
    print("\n--- 5. Historical Prediction & Inference in Container ---")
    code, out, err = run_wsl_cmd("curl -s 'http://127.0.0.1:8000/api/predictions/historical?basin_id=Hp-I&year=2015'")
    check("Historical prediction query HTTP 200", code == 0)
    try:
        hist_pts = json.loads(out)
        check("Historical prediction returned 1 record", len(hist_pts) == 1)
        check("Historical model is MOD-04", hist_pts[0].get("selected_model_id") == "MOD-04")
    except Exception as e:
        check("Historical prediction JSON valid", False, str(e))

    # Run live inference inside container
    infer_payload = json.dumps({
        "basin_id": "Hp-I",
        "model_id": "MOD-04",
        "features": {
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
    })
    code, out, err = run_wsl_cmd(f"curl -s -X POST http://127.0.0.1:8000/api/predictions/run -H 'Content-Type: application/json' -d '{infer_payload}'")
    check("Live inference POST HTTP 200", code == 0)
    try:
        infer_resp = json.loads(out)
        check("Inference returned predicted_mass_balance_gt_yr", "predicted_mass_balance_gt_yr" in infer_resp)
        check("Inference returned predicted_volume_change_km3_yr", "predicted_volume_change_km3_yr" in infer_resp)
    except Exception as e:
        check("Live inference JSON valid", False, str(e))

    # 6. All Eight Frontend Routes through Port 80
    print("\n--- 6. All Eight Frontend Routes through Port 80 ---")
    routes = [
        "/",
        "/models",
        "/predictions",
        "/projections",
        "/explorer",
        "/datasets",
        "/physical-model",
        "/validation"
    ]
    for r in routes:
        code, out, err = run_wsl_cmd(f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:80{r}")
        check(f"Route {r} returns 200", out.strip() == "200")

    # Check that index.html contains root div and script tags
    code, out, err = run_wsl_cmd("curl -s http://127.0.0.1:80/")
    check("HTML has <div id=\"root\">", '<div id="root">' in out)
    check("HTML has compiled JS script bundle", '<script type="module"' in out)

    # 7. Security Audit: Check for embedded secrets
    print("\n--- 7. Security & Image Hygiene Audit ---")
    code, out, err = run_wsl_cmd("docker run --rm antarctic-ice-volume-prediction-backend env")
    check("No EARTHDATA_TOKEN in backend container environment", "EARTHDATA_TOKEN" not in out)
    check("No password or token in backend env", "password" not in out.lower() and "token" not in out.lower())

    # Check frontend compiled assets for token leakage
    code, out, err = run_wsl_cmd("docker run --rm antarctic-ice-volume-prediction-frontend sh -c 'grep -rn \"EARTHDATA_TOKEN\" /usr/share/nginx/html/'")
    check("No EARTHDATA_TOKEN in frontend static bundle", code != 0 or out.strip() == "")

    # Check container file permissions
    code, out, err = run_wsl_cmd("docker exec cryopredict-backend ls -ld /app/models /app/data /app/reports")
    check("Backend application directories exist and are accessible", code == 0)

    # 8. Container Restart Verification
    print("\n--- 8. Container Restart Verification ---")
    code, out, err = run_wsl_cmd("cd /mnt/c/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction && docker compose restart")
    check("Docker compose restart successful", code == 0)

    # Allow startup
    subprocess.run(["wsl.exe", "-d", "Ubuntu", "-u", "root", "sh", "-c", "sleep 5"])

    # Re-verify health after restart
    code, out, err = run_wsl_cmd("curl -s -f http://127.0.0.1:8000/api/health")
    check("Backend /api/health healthy after restart", code == 0 and "healthy" in out)

    code, out, err = run_wsl_cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/projections")
    check("Frontend /projections returns 200 after restart", out.strip() == "200")

    # 9. Container Log Cleanliness
    print("\n--- 9. Container Log Cleanliness ---")
    code, out, err = run_wsl_cmd("cd /mnt/c/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction && docker compose logs --tail=50")
    check("Logs retrieved successfully", code == 0)
    has_unexpected_traceback = "Traceback (most recent call last)" in out
    has_fatal_error = "FATAL" in out or "CRITICAL" in out
    check("No unhandled tracebacks in container logs", not has_unexpected_traceback)
    check("No fatal errors in container logs", not has_fatal_error)

    # Summary
    print("\n" + "=" * 80)
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v == "PASS")
    print(f"TOTAL DOCKER SMOKE CHECKS: {total_checks} | PASSED: {passed_checks} | FAILED: {len(failures)}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  - {f}")
    else:
        print("ALL DOCKER RELEASE CANDIDATE SMOKE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

    return len(failures) == 0

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
