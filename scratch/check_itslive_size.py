"""
Check size of ITS_LIVE_velocity_120m_RGI19A_2015_v02.nc.
"""
import s3fs

fs = s3fs.S3FileSystem(anon=True)
info2 = fs.info('its-live-data/velocity_mosaic/v2/annual/ITS_LIVE_velocity_120m_RGI19A_2015_v02.nc')
print("v2 size:", info2['size'] / (1024*1024), "MB")

info21 = fs.info('its-live-data/velocity_mosaic/v2.1/annual/ITS_LIVE_velocity_120m_RGI19A_2015_V02.1.nc')
print("v2.1 size:", info21['size'] / (1024*1024), "MB")

