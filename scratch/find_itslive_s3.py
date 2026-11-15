"""
Find ITS_LIVE Antarctic mosaic on AWS S3 using s3fs anonymous.
"""
import s3fs

fs = s3fs.S3FileSystem(anon=True)

try:
    print("Listing its-live-data/ :")
    top = fs.ls('its-live-data')
    for item in top:
        print(" ", item)
except Exception as e:
    print("Error listing top:", e)

try:
    print("\nSearching for mosaics:")
    for item in fs.ls('its-live-data/velocity_mosaic'):
        print(" ", item)
except Exception as e:
    print("Error listing velocity_mosaic:", e)
