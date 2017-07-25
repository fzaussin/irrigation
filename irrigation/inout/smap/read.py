import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

import pygeogrids
from pygeogrids.netcdf import load_grid
from smap_io.interface import SMAPTs
import interp

# init paths
path = '/home/fzaussin/SMAP_L3_P_v3'
grid = pygeogrids.netcdf.load_grid('/home/fzaussin/SMAP_L3_P_v3/grid.nc')


# find gpi
lat = 41.625
lon = 60.625
gpi_nn = grid.find_nearest_gpi(lon=lon, lat=lat)
print gpi_nn
gpi = gpi_nn[0]

# read ts
smap = SMAPTs(path)
ts = smap.read(gpi)
# TODO: whats up with sm_error ??
ts = ts['soil_moisture']
ts.plot(x='x', y='y', style=".", color='orange')

# apply gap filling
smap_gapfill = interp.fill_gaps(ts, 5)

# plot
title = 'SMAP SSM (lon={}, lat={})'.format(lon,lat)
ax = smap_gapfill.plot(title=title, color='lightblue')
ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
ax.set_xlabel('Datetime')

plt.show()
