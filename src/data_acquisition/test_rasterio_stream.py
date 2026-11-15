import rasterio
from rasterio.windows import from_bounds

url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"

print("Attempting to inspect remote GeoTIFF via Rasterio...")
try:
    with rasterio.open(url) as src:
        print("Successfully opened remote GeoTIFF!")
        print("CRS:", src.crs)
        print("Dimensions (width, height):", src.width, src.height)
        print("Bounds:", src.bounds)
        print("Transform:", src.transform)
        print("NoData:", src.nodata)
        print("Data types:", src.dtypes)
        print("Block shapes / tiling:", src.block_shapes)
        
        # Test window calculation for Antarctic Peninsula bounds
        # [-2700000, 250000, -1400000, 1950000]
        window = from_bounds(-2700000, 250000, -1400000, 1950000, src.transform)
        print("Calculated Peninsula Window:", window)
except Exception as e:
    print("Could not stream directly via vsicurl:", e)

