import os
import requests
import time

def download_file(url, dest_path, description):
    if os.path.exists(dest_path):
        print(f"{description} already exists at {dest_path} ({os.path.getsize(dest_path)} bytes)")
        return
    
    print(f"\n--- Starting download: {description} ---")
    print(f"URL: {url}")
    print(f"Destination: {dest_path}")
    
    t0 = time.time()
    resp = requests.get(url, stream=True, timeout=30)
    total_size = int(resp.headers.get("content-length", 0))
    print(f"Total size: {total_size / 1e6:.2f} MB")
    
    downloaded = 0
    last_print = time.time()
    
    part_path = dest_path + ".part"
    with open(part_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=2 * 1024 * 1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if time.time() - last_print > 5:
                    pct = (downloaded / total_size * 100) if total_size > 0 else 0
                    rate = downloaded / (time.time() - t0) / 1e6
                    print(f"Progress: {downloaded / 1e6:.1f} / {total_size / 1e6:.1f} MB ({pct:.1f}%) at {rate:.2f} MB/s")
                    last_print = time.time()
                    
    os.rename(part_path, dest_path)
    print(f"Successfully downloaded {description} in {time.time() - t0:.1f} seconds! Saved to: {dest_path}")

if __name__ == "__main__":
    raw_dir = "antarctic-ice-volume-prediction/data/raw/bedmap3"
    os.makedirs(raw_dir, exist_ok=True)
    
    # 1. Download bm3_thickness.tif (361 MB)
    thick_url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"
    download_file(thick_url, os.path.join(raw_dir, "bm3_thickness.tif"), "Bedmap3 Ice Thickness")
    
    # 2. Download bm3_masks.tif
    mask_url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_masks.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM19tYXNrcy50aWY="
    download_file(mask_url, os.path.join(raw_dir, "bm3_masks.tif"), "Bedmap3 Masks")
    
    # 3. Download bm3_thickness_uncertainty.tif
    unc_url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness_uncertainty.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3NfdW5jZXJ0YWludHkudGlm"
    download_file(unc_url, os.path.join(raw_dir, "bm3_thickness_uncertainty.tif"), "Bedmap3 Thickness Uncertainty")

