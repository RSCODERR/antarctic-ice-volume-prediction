"""
Check RGI19 in ITS_LIVE annual.
"""
import s3fs

fs = s3fs.S3FileSystem(anon=True)
items = fs.ls('its-live-data/velocity_mosaic/v2/annual')
rgi19 = [it for it in items if 'RGI19' in it.upper() or 'ANT' in it.upper()]
print(f"RGI19 / ANT in v2/annual: {len(rgi19)}")
for it in rgi19:
    print(" ", it)

items21 = fs.ls('its-live-data/velocity_mosaic/v2.1/annual')
rgi19_21 = [it for it in items21 if 'RGI19' in it.upper() or 'ANT' in it.upper()]
print(f"\nRGI19 / ANT in v2.1/annual: {len(rgi19_21)}")
for it in rgi19_21:
    print(" ", it)

