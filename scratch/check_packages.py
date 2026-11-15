for pkg in ['xarray', 'rasterio', 'h5py', 'gdal', 'geopandas', 'shapely', 'pyproj', 'scipy', 'matplotlib', 'pandas', 'PIL']:
    try:
        mod = __import__(pkg)
        print(f"{pkg}: {getattr(mod, '__version__', 'installed')}")
    except ImportError:
        print(f"{pkg}: NOT INSTALLED")

