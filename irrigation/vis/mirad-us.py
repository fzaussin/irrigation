import xarray as xr
import numpy as np
from vis.spatialplot import spatial_plot


mirad = xr.open_dataset('/home/fzaussin/shares/home/mirad-25km/mirad25km.nc')

lon = mirad.variables['lon'].data
lat = mirad.variables['lat'].data
lons, lats = np.meshgrid(lon, lat)
irrigation = mirad.variables['irrigation'] / 100
mirad.plot()

print lons.shape, lats.shape, irrigation.shape


spatial_plot(irrigation, lons, lats)
