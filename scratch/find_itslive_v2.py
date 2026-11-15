"""
List contents of velocity_mosaic/v2 and v2.1.
"""
import s3fs

fs = s3fs.S3FileSystem(anon=True)

for prefix in ['its-live-data/velocity_mosaic/v2', 'its-live-data/velocity_mosaic/v2.1']:
    print(f"\nListing {prefix}:")
    try:
        items = fs.ls(prefix)
        for it in items[:10]:
            print(" ", it)
    except Exception as e:
        print("  Error:", e)

