# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 10:42:39 2016

@author: wpreimes
"""

import numpy as np
import pandas as pd

from smecv.input.common_format import CCIDs
from rsdata.ECMWF.interface import ERALAND_g2ze


def era_land_ts(gpi_era, start_date, end_date, temp_res='daily_mean'):
    """
    Read ERA-LAND Soil Moisture Timeseries (Parameter=39) at ERA Gpi
    """

    ts = ERALAND_g2ze().read_ts(gpi_era)[start_date:end_date]

    if ts.empty:
        error_message = 'No data available at this date.'
        return error_message

    if temp_res == 'daily_mean':
        ts = ts.resample('D').mean()
        return ts
    else:
        return ts


class QDEGdata(object):
    """
    changed path in "..\smecv\grids\ecv.py" to grid file
    Benötigt ECV_CCI_gridv4.nc
    """
    def __init__(self):
        """initialize data paths"""
        path_ascat = '/home/fzaussin/shares/users/Irrigation/Data/input/ascat-a'
        path_amsre = '/home/fzaussin/shares/users/Irrigation/Data/input/amsr2'
        path_amsr2 = '/home/fzaussin/shares/users/Irrigation/Data/input/amsre'

        self.ascat = CCIDs(path_ascat)
        self.amsre = CCIDs(path_amsre)
        self.amsr2 = CCIDs(path_amsr2)

    def read_gpi(self,gpi,startdate,enddate,*products):
        """

        :param gpi: grid point index on quarter degree grid
        :param startdate:
        :param enddate:
        :param products:
        :return: pd.DataFrame
            Holds time series of the specified products from startdate to enddate
        """
        # initialize data container
        data_group = pd.DataFrame(index=pd.date_range(start=startdate,end=enddate))

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

        return data_group

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    data = QDEGdata()
    ts = data.read_gpi(710232, '2007-01-01', '2013-12-31', 'ascat', 'amsre', 'amsr2')
    print ts
    ts.plot()
    plt.show()