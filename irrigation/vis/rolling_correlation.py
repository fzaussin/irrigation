# -*- coding: utf-8 -*-

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use(['ggplot', 'seaborn-poster'])
from pygeogrids.grids import genreg_grid
from irrigation.prep.timeseries import prepare

qdeg_grid = genreg_grid(
    grd_spc_lat=0.25,
    grd_spc_lon=0.25).to_cell_grid()

def qdeg2lonlat(gpi):
    """
    Return lon and lat for a given 0.25° grid point index
    :param gpi:
    :return: lon, lat
    """
    lon, lat = qdeg_grid.gpi2lonlat(gpi)
    return lon, lat * (-1)

if __name__=='__main__':

    """
    cali: 726000 - California Central Valley
    mississ: 723239 - Mississippi Delta
    idaho: 763461 - Snake River Valley, Idaho
    nebraska: 750568 - Plains of Nebraska
    georgia: 701663
    """
    gpi = 730445

    location = 'Mississippi Delta'
    lon, lat = qdeg2lonlat(gpi)

    ts = prepare(gpi=gpi,
                start_date='2007-01-01',
                end_date='2016-12-31',
                models=['merra'],
                satellites=['ascatrecklessrom'],#, 'amsr2', 'smapv4'],
                kind='clim')
                #window=35)

    # rename cols for manuscript
    ts.rename(columns={'merra': 'MERRA',
                       'ascat_reckless_rom': 'ASCAT'},
              inplace=True)

    # calc rolling correlation
    corr = ts['ASCAT'].rolling(35).corr(ts['MERRA'])

    plt.figure(figsize=(15,10))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)

    title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                          lat=str(lat),
                                                          lon=str(lon))
    # first row
    ts['MERRA'].plot(ax=ax1, label='MERRA',title=title, ylim=(0.2,0.4))
    ts['ASCAT'].plot(ax=ax1, label='ASCAT')
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

    # second row
    corr.plot(ax=ax2, color='black')
    ax2.set_ylabel("Rolling correlation")
    ax2.set_xlabel("DOY")

    # plot
    plt.tight_layout()
    plt.show()