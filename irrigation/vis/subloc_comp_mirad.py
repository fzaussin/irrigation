import pandas as pd
import numpy as np
import xarray as xr
from irrigation.vis.spatialplot import spatial_plot_quarter_grid

mirad = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/validation/mirad_downscaling/mirad-25km/mirad25kmv2_lat_lon_gpi_025degrees.csv')
print mirad.head()
#mirad['irrigation'].replace(0.0, np.nan, inplace=True)
print mirad.head()

spatial_plot_quarter_grid(mirad,
                          tags=['irrigation'],
                          tight=True,
                          cmap='Blues',
                          cbrange=(0,100),
                          title='Irrigation Intensity (%)')
