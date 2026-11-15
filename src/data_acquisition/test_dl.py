import requests

def test_downloads():
    print("Testing NSIDC Basins download...")
    url_nsidc = "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0709/2/1992/02/07/Basins_IMBIE_Antarctica_v02.shp"
    r = requests.get(url_nsidc, allow_redirects=False, timeout=10)
    print("NSIDC status:", r.status_code, "Location:", r.headers.get("Location"))

    print("\nTesting RAMADDA bm3_thickness.tif...")
    ramadda_id = "synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"
    url_ramadda = f"https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness.tif?entryid={ramadda_id}"
    r2 = requests.head(url_ramadda, allow_redirects=True, timeout=10)
    print("RAMADDA status:", r2.status_code, "Content-Length:", r2.headers.get("Content-Length"), "Content-Type:", r2.headers.get("Content-Type"))

if __name__ == "__main__":
    test_downloads()

