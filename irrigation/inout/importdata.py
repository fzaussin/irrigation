# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd

from smecv.input.common_format import CCIDs
from rsdata.ECMWF.interface import ERALAND_g2ze
from rsdata.GLDAS_NOAH.interface import GLDAS025v2Ts

from pynetcf.time_series import GriddedNcContiguousRaggedTs
import pygeogrids.netcdf as ncgrids

# generate qdeg grid once
from pygeogrids.grids import genreg_grid
qdeg_grid = genreg_grid(grd_spc_lat=0.25, grd_spc_lon=0.25).to_cell_grid()

# generate waro grid
warp_path = '/home/fzaussin/shares/radar/Datapool_processed/WARP/datasets/reckless_rom/R1AB/080_ssm/netcdf'
warp_grid_path = '/home/fzaussin/shares/radar/Datapool_processed/WARP/ancillary/warp5_grid/TUW_WARP5_grid_info_2_1.nc'
warp_grid = ncgrids.load_grid(warp_grid_path)
io_ascat = GriddedNcContiguousRaggedTs(path=warp_path, grid=warp_grid)


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

def ascat_vegcorr(gpi):
    """Read ascat data with new vegetation correction"""
    lon, lat = qdeg2lonlat(gpi)
    ascat_ts = io_ascat.read(lon, lat)
    return ascat_ts


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

    def read_gpi(self, gpi, start_date, end_date, model, satellites):
        """
        :param gpi: grid point index on quarter degree grid
        :param start_date:
        :param end_date:
        :param products:
        :return: pd.DataFrame
            Holds time series of the specified products from startdate to enddate
        """
        #TODO: raise error if qdeg gpi not valid

        # initialize data container
        data_group = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))

        if model == 'eraland':
            ts_era = era_land_ts(gpi)
            # error handling
            if ts_era is None:
                print 'No eraland data for gpi %0i' % gpi
                ts_era = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_era = ts_era[start_date:end_date]
                # append to data_group
            # scale percentage values from [0,1] to [0,100]
            data_group['eraland'] = ts_era * 100

        elif model == 'gldas':
            ts_gldas = GLDAS025v2Ts().read_ts(gpi)
            # error handling
            if ts_gldas is None:
                print 'No gldas data for gpi %0i' % gpi
                ts_gldas = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_gldas = ts_gldas[start_date:end_date]
                # append to data_group
            data_group['gldas'] = ts_gldas
        else:
            pass

        if 'amsre' in satellites:
            # read amsr2 data
            ts_amsre = self.amsre.read(gpi)
            if ts_amsre is None:
                print 'No amsre data for gpi %0i' % gpi
                ts_amsre = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_amsre = ts_amsre[ts_amsre.flag==0]['sm'][start_date:end_date]
            # append to data_group
            ts_amsre.index=ts_amsre.index.date
            data_group['amsre'] = ts_amsre

        # check for keywords 'ascat', 'amsre' and 'amsr2' and append ts to data_group
        if 'ascat' in satellites:
            ts_ascat = self.ascat.read(gpi)
            # error handling
            if ts_ascat is None:
                print 'No ascat data for gpi %0i' % gpi
                ts_ascat = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_ascat = ts_ascat[ts_ascat.flag==0]['sm'][start_date:end_date]
            # append to data_group
            ts_ascat.index=ts_ascat.index.date
            data_group['ascat'] = ts_ascat

        if 'ascat_vegcorr' in satellites:
            ts_ascat_vegcorr = ascat_vegcorr(gpi)
            if ts_ascat_vegcorr is None:
                print 'No veg_corr ascat data for gpi %0i' % gpi
                ts_ascat_vegcorr = pd.Series(
                    index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_ascat_vegcorr = ts_ascat_vegcorr[(ts_ascat_vegcorr['proc_flag'] <= 2) & (ts_ascat_vegcorr['ssf'] == 1)][
                    'sm']
                # drop hours, mins, secs
                ts_ascat_vegcorr.index = ts_ascat_vegcorr.index.normalize()
            # append to data group
            #ts_ascat_vegcorr.index = ts_ascat_vegcorr.index.date
            print ts_ascat_vegcorr
            ts_ascat_vegcorr = ts_ascat_vegcorr.resample('D').mean()
            data_group['ascat_vegcorr'] = ts_ascat_vegcorr

        if 'amsr2' in satellites:
            # read amsr2 data
            ts_amsr2 = self.amsr2.read(gpi)
            # error handling
            if ts_amsr2 is None:
                print 'No amsr2 data for gpi %0i' % gpi
                ts_amsr2 = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_amsr2 = ts_amsr2[ts_amsr2.flag==0]['sm'][start_date:end_date]
            # append to data_group
            ts_amsr2.index=ts_amsr2.index.date
            data_group['amsr2'] = ts_amsr2

        return data_group

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    data = QDEGdata()
    ts_test = data.read_gpi(750602, '2007-01-01', '2015-12-31',
                                 model='eraland',
                                 satellites=['ascat', 'ascat_vegcorr', 'amsr2'])
    ts_test.plot(title='test')
    plt.show()
