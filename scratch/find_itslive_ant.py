"""
List ANT files in velocity_mosaic/v2/annual and v2.1/annual.
"""
import s3fs

fs = s3fs.S3FileSystem(anon=True)

for p in ['its-live-data/velocity_mosaic/v2/annual', 'its-live-data/velocity_mosaic/v2.1/annual']:
    print(f"\nListing {p} with ANT:")
    try:
        items = fs.ls(p)
        ant_items = [it for it in items if 'ANT' in it.upper() or '2015' in it]
        print(f"Total items: {len(items)}, ANT/2015 items: {len(ant_items)}")
        for it in ant_items[:15]:
            print(" ", it)
    except Exception as e:
        print("  Error:", e)

