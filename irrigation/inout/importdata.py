# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd

from smecv.input.common_format import CCIDs
from rsdata.ECMWF.interface import ERALAND_g2ze

# generate qdeg grid once
from pygeogrids.grids import genreg_grid
qdeg_grid = genreg_grid(grd_spc_lat=0.25, grd_spc_lon=0.25).to_cell_grid()


def qdeg2lonlat(gpi_quarter):
    """"""
    lon, lat = qdeg_grid.gpi2lonlat(gpi_quarter)
    return (lon, lat*(-1))

def era_land_ts(gpi):
    """Read daily ERA-Interim/Land Soil Moisture Timeseries (Parameter=39)"""
    era = ERALAND_g2ze()
    # find nearest era gpi
    lon, lat = qdeg2lonlat(gpi)
    gpi_era = era.get_nearest_gp_info(lon, lat)[0]

    return era.read_ts(gpi_era)


class QDEGdata(object):
    """
    changed path in "..\smecv\grids\ecv.py" to grid file
    Benötigt ECV_CCI_gridv4.nc
    """
    def __init__(self):
        """initialize data paths"""
        path_amsre = '/home/fzaussin/shares/users/Irrigation/Data/input/amsre'
        path_ascat = '/home/fzaussin/shares/users/Irrigation/Data/input/ascat-a'
        path_amsr2 = '/home/fzaussin/shares/users/Irrigation/Data/input/amsr2'

        self.amsre = CCIDs(path_amsre)
        self.ascat = CCIDs(path_ascat)
        self.amsr2 = CCIDs(path_amsr2)

    def read_gpi(self, gpi, startdate, enddate, *products):
        """

        :param gpi: grid point index on quarter degree grid
        :param startdate:
        :param enddate:
        :param products:
        :return: pd.DataFrame
            Holds time series of the specified products from startdate to enddate
        """
        #TODO: raise error if qdeg gpi not valid

        # initialize data container
        data_group = pd.DataFrame(index=pd.date_range(start=startdate,end=enddate))

        if 'eraland' in products:
            ts_era = era_land_ts(gpi)
            # error handling
            if ts_era is None:
                print 'No eraland data for gpi %0i' % gpi
                ts_era = pd.Series(index=pd.date_range(start=startdate, end=enddate))
            else:
                ts_era = ts_era[startdate:enddate]
                # append to data_group
            # scale percentage values from [0,1] to [0,100]
            data_group['eraland'] = ts_era * 100

        if 'amsre' in products:
            # read amsr2 data
            ts_amsre = self.amsre.read(gpi)
            if ts_amsre is None:
                print 'No amsre data for gpi %0i' % gpi
                ts_amsre = pd.Series(index=pd.date_range(start=startdate,end=enddate))
            else:
                ts_amsre = ts_amsre[ts_amsre.flag==0]['sm'][startdate:enddate]
            # append to data_group
            ts_amsre.index=ts_amsre.index.date
            data_group['amsre'] = ts_amsre

        # check for keywords 'ascat', 'amsre' and 'amsr2' and append ts to data_group
        if 'ascat' in products:
            ts_ascat = self.ascat.read(gpi)
            # error handling
            if ts_ascat is None:
                print 'No ascat data for gpi %0i' % gpi
                ts_ascat = pd.Series(index=pd.date_range(start=startdate,end=enddate))
            else:
                ts_ascat = ts_ascat[ts_ascat.flag==0]['sm'][startdate:enddate]
            # append to data_group
            ts_ascat.index=ts_ascat.index.date
            data_group['ascat'] = ts_ascat

        if 'amsr2' in products:
            # read amsr2 data
            ts_amsr2 = self.amsr2.read(gpi)
            # error handling
            if ts_amsr2 is None:
                print 'No amsr2 data for gpi %0i' % gpi
                ts_amsr2 = pd.Series(index=pd.date_range(start=startdate,end=enddate))
            else:
                ts_amsr2 = ts_amsr2[ts_amsr2.flag==0]['sm'][startdate:enddate]
            # append to data_group
            ts_amsr2.index=ts_amsr2.index.date
            data_group['amsr2'] = ts_amsr2

        return data_group

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    data = QDEGdata()
    ts = data.read_gpi(707349, '2007-01-01', '2013-12-31', 'eraland', 'ascat', 'amsre', 'amsr2')
    print ts
    ts.plot()
    plt.show()
