"""
Search for smaller ITS_LIVE products or 240m mosaics.
"""
import s3fs

fs = s3fs.S3FileSystem(anon=True)
items = fs.ls('its-live-data/velocity_mosaic/v2/annual')
m240 = [it for it in items if '240' in it]
print(f"240m items in v2/annual: {len(m240)}")
for it in m240[:10]:
    print(" ", it)

# Also check if there are sub-tiles for RGI19
rgi19_sub = [it for it in items if 'RGI19' in it and '120m' not in it]
print(f"Non-120m RGI19 in v2/annual: {len(rgi19_sub)}")
for it in rgi19_sub[:10]:
    print(" ", it)

