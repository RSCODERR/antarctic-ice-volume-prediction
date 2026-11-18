import os
import subprocess
import time

def capture_all():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    temp_dir = os.path.join(os.environ.get("TEMP", "C:/tmp"), "chrome_scr_temp")
    os.makedirs(temp_dir, exist_ok=True)

    fig_dir = r"c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction\figures"
    os.makedirs(fig_dir, exist_ok=True)

    shots = [
        {
            "name": "stage7_2_future_projections_default.png",
            "url": "http://127.0.0.1:5173/projections",
            "desc": "Default View (RCP8.5, Domain A, Delta_VAF)"
        },
        {
            "name": "stage7_2_future_projections_iipp_drawdown.png",
            "url": "http://127.0.0.1:5173/projections?scenario=RCP8.5&region=I-Ipp&metric=sle&show90=true",
            "desc": "Western Marine Drawdown (I-Ipp, SLE metric, 90% Risk Interval)"
        },
        {
            "name": "stage7_2_future_projections_ssp245_synthesis.png",
            "url": "http://127.0.0.1:5173/projections?scenario=SSP2-4.5&region=Domain_A&metric=vaf",
            "desc": "Scaled Synthesis Scenario (SSP2-4.5, SCALED_EMULATOR_SYNTHESIS watermark)"
        }
    ]

    for s in shots:
        out_file = os.path.join(fig_dir, s["name"])
        cmd = [
            chrome_path,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={temp_dir}",
            f"--screenshot={out_file}",
            "--window-size=1440,2400",
            "--virtual-time-budget=6000",
            s["url"]
        ]
        print(f"Capturing: {s['desc']} -> {s['name']}...")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        exists = os.path.exists(out_file)
        size = os.path.getsize(out_file) if exists else 0
        print(f"  Result: exists={exists}, size={size:,} bytes")

if __name__ == "__main__":
    capture_all()
