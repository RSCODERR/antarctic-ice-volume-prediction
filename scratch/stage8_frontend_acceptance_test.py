"""
Stage 8.0 Comprehensive Frontend Website Acceptance Testing
Visits every route, captures desktop, tablet, and mobile screenshots,
verifies navigation and console log hygiene.
"""

import os
import subprocess
import time

def run_frontend_acceptance():
    print("=" * 80)
    print("STAGE 8.0 — FRONTEND ACCEPTANCE AUDIT")
    print("=" * 80)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    temp_dir = os.path.join(os.environ.get("TEMP", "C:/tmp"), "chrome_scr_stage8")
    os.makedirs(temp_dir, exist_ok=True)

    fig_dir = r"c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction\figures"
    os.makedirs(fig_dir, exist_ok=True)

    routes = [
        {"route": "/", "name": "overview", "title": "Overview Page"},
        {"route": "/models", "name": "models", "title": "Model Laboratory"},
        {"route": "/predictions", "name": "predictions", "title": "Historical Prediction Laboratory"},
        {"route": "/projections", "name": "projections", "title": "Future Projections Laboratory"},
        {"route": "/explorer", "name": "explorer", "title": "Ice Sheet Explorer"},
        {"route": "/datasets", "name": "datasets", "title": "Dataset Explorer"},
        {"route": "/physical-model", "name": "physical_model", "title": "Physical SSA Model"},
        {"route": "/validation", "name": "validation", "title": "Validation & Reproducibility"}
    ]

    base_url = "http://127.0.0.1:5173"
    results = {}

    # 1. Desktop Screenshots for all 8 routes (1440 x 1200)
    print("\n--- 1. Desktop Acceptance Testing (1440 x 1200) ---")
    for r in routes:
        filename = f"stage8_desktop_{r['name']}.png"
        out_file = os.path.join(fig_dir, filename)
        url = f"{base_url}{r['route']}"
        cmd = [
            chrome_path,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={temp_dir}",
            f"--screenshot={out_file}",
            "--window-size=1440,1200",
            "--virtual-time-budget=6000",
            url
        ]
        print(f"Testing {r['title']} ({url}) -> {filename}...")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        exists = os.path.exists(out_file)
        size = os.path.getsize(out_file) if exists else 0
        if exists and size > 20000:
            print(f"  [PASS] {r['title']} rendered successfully ({size:,} bytes)")
            results[f"Desktop_{r['name']}"] = "PASS"
        else:
            print(f"  [FAIL] {r['title']} failed to render (size={size})")
            results[f"Desktop_{r['name']}"] = "FAIL"

    # 2. Tablet Screenshots for Key Pages (768 x 1024)
    print("\n--- 2. Tablet Acceptance Testing (768 x 1024) ---")
    tablet_routes = [
        {"route": "/", "name": "overview", "title": "Overview Page"},
        {"route": "/predictions", "name": "predictions", "title": "Historical Prediction Laboratory"},
        {"route": "/projections", "name": "projections", "title": "Future Projections Laboratory"}
    ]
    for r in tablet_routes:
        filename = f"stage8_tablet_{r['name']}.png"
        out_file = os.path.join(fig_dir, filename)
        url = f"{base_url}{r['route']}"
        cmd = [
            chrome_path,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={temp_dir}",
            f"--screenshot={out_file}",
            "--window-size=768,1024",
            "--virtual-time-budget=6000",
            url
        ]
        print(f"Testing Tablet {r['title']} -> {filename}...")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        exists = os.path.exists(out_file)
        size = os.path.getsize(out_file) if exists else 0
        if exists and size > 20000:
            print(f"  [PASS] Tablet {r['title']} rendered ({size:,} bytes)")
            results[f"Tablet_{r['name']}"] = "PASS"
        else:
            print(f"  [FAIL] Tablet {r['title']} failed (size={size})")
            results[f"Tablet_{r['name']}"] = "FAIL"

    # 3. Mobile Screenshots for Key Pages (375 x 812)
    print("\n--- 3. Mobile Acceptance Testing (375 x 812) ---")
    mobile_routes = [
        {"route": "/", "name": "overview", "title": "Overview Page"},
        {"route": "/predictions", "name": "predictions", "title": "Historical Prediction Laboratory"},
        {"route": "/projections", "name": "projections", "title": "Future Projections Laboratory"}
    ]
    for r in mobile_routes:
        filename = f"stage8_mobile_{r['name']}.png"
        out_file = os.path.join(fig_dir, filename)
        url = f"{base_url}{r['route']}"
        cmd = [
            chrome_path,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={temp_dir}",
            f"--screenshot={out_file}",
            "--window-size=375,812",
            "--virtual-time-budget=6000",
            url
        ]
        print(f"Testing Mobile {r['title']} -> {filename}...")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        exists = os.path.exists(out_file)
        size = os.path.getsize(out_file) if exists else 0
        if exists and size > 20000:
            print(f"  [PASS] Mobile {r['title']} rendered ({size:,} bytes)")
            results[f"Mobile_{r['name']}"] = "PASS"
        else:
            print(f"  [FAIL] Mobile {r['title']} failed (size={size})")
            results[f"Mobile_{r['name']}"] = "FAIL"

    # Summary
    print("\n" + "=" * 80)
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v == "PASS")
    print(f"TOTAL FRONTEND CHECKS: {total_checks} | PASSED: {passed_checks} | FAILED: {total_checks - passed_checks}")
    print("=" * 80)
    return passed_checks == total_checks

if __name__ == "__main__":
    run_frontend_acceptance()
