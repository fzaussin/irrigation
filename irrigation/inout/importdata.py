# -*- coding: utf-8 -*-

import os
import pandas as pd

# Models
from gldas.interface import GLDASTs
from rsdata.ECMWF.interface import ERALAND_g2ze
from irrigation.inout.merra.interface import MERRA2_Ts
# Satellites
from smecv.input.common_format import CCIDs
from pynetcf.time_series import GriddedNcContiguousRaggedTs
from smap_io.interface import SMAPTs
# Grids
from pygeogrids.grids import genreg_grid
import pygeogrids.netcdf as ncgrids


class QDEGdata(object):
    """
    Class for harmonized reading of several model and satellite soil moisture
    data sets. When initialized, the objects implementing the read functions
    are created. Every subsequent call of read_gpi uses these objects.

    Note: Needs ECV_CCI_gridv4.nc to read the CCIDs
    """

    def __init__(self):
        """
        Define paths to data directories and initialize data objects
        """
        path_warp_grid = ncgrids.load_grid(
            ('/home/fzaussin/shares/radar/Datapool_processed'
             '/WARP/ancillary/warp5_grid/TUW_WARP5_grid_info_2_1.nc'))

        path_amsre = '/home/fzaussin/shares/users/Irrigation/Data/input/amsre'
        path_amsr2 = '/home/fzaussin/shares/users/Irrigation/Data/input/amsr2'
        path_ascat = '/home/fzaussin/shares/users/Irrigation/Data/input/ascat-a'

        path_ascat_reckless_rom = ('/home/fzaussin/shares/radar/'
                                   'Datapool_processed/WARP/datasets/'
                                   'reckless_rom/R1AB/080_ssm/netcdf')
        path_smap = '/home/fzaussin/SMAP_L3_P_v3'

        path_gldas = ('/home/fzaussin/shares/radar/Datapool_processed/'
                      'GLDAS/GLDAS_NOAH025_3H.2.1/datasets')
        path_merra = '/home/fzaussin/merra-sfmc'

        # init data objects
        self.qdeg_grid = genreg_grid(
            grd_spc_lat=0.25,
            grd_spc_lon=0.25).to_cell_grid()

        self.amsre = CCIDs(path_amsre)
        self.amsr2 = CCIDs(path_amsr2)
        self.ascat = CCIDs(path_ascat)
        self.ascat_reckless_rom = GriddedNcContiguousRaggedTs(
            path=path_ascat_reckless_rom, grid=path_warp_grid)
        self.smap = SMAPTs(path_smap)

        self.eraland = ERALAND_g2ze()
        self.merra = MERRA2_Ts(ts_path=path_merra)
        self.gldas = GLDASTs(ts_path=path_gldas)

    def qdeg2lonlat(self, gpi):
        """
        Return lon and lat for a given 0.25° grid point index
        :param gpi:
        :return: lon, lat
        """
        lon, lat = self.qdeg_grid.gpi2lonlat(gpi)
        return lon, lat * (-1)

    def read_gpi(self, gpi, start_date, end_date,
                 models=None, satellites=None):
        """
        Read model and/or satellite soil moisture data at qdeg gpi between
        a specified date range.
        :param gpi: grid point index on quarter degree grid
        :param start_date:
        :param end_date:
        :param products:
        :return: pd.DataFrame
            Holds time series of the specified products from startdate to enddate
        """
        # get lon, lat for gpi
        lon, lat = self.qdeg2lonlat(gpi)
        # initialize data container
        data_group = pd.DataFrame(
            index=pd.date_range(
                start=start_date,
                end=end_date))

        # MODELS
        if 'eraland' in models:
            ts_era = self.eraland.read_ts(lon, lat)
            # error handling
            if ts_era is None:
                print 'No eraland data for gpi %0i' % gpi
                ts_era = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_era = ts_era[start_date:end_date]
                # append to data_group
            # scale percentage values from [0,1] to [0,100]
            data_group['eraland'] = ts_era * 100

        if 'gldas' in models:
            ts_gldas = self.gldas.read(lon, lat)
            # error handling
            if ts_gldas is None:
                print 'No gldas data for gpi %0i' % gpi
                ts_gldas = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_gldas = ts_gldas[start_date:end_date]
                # append to data_group
            data_group['gldas'] = ts_gldas['SoilMoi0_10cm_inst']

        if 'merra' in models:
            ts_merra = self.merra.read(lon, lat)
            # error handling
            if ts_merra is None:
                print 'No merra data for gpi %0i' % gpi
                ts_merra = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_merra = ts_merra[start_date:end_date]
                # append to data_group
            data_group['merra'] = ts_merra.resample('D').mean() * 100

        # SATELLITES
        if 'amsre' in satellites:
            # read amsr2 data
            ts_amsre = self.amsre.read(lon, lat)
            if ts_amsre is None:
                print 'No amsre data for gpi %0i' % gpi
                ts_amsre = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_amsre = ts_amsre[ts_amsre.flag ==
                                    0]['sm'][start_date:end_date]
            # append to data_group
            ts_amsre.index = ts_amsre.index.date
            data_group['amsre'] = ts_amsre

        if 'ascat' in satellites:
            ts_ascat = self.ascat.read(lon, lat)
            # error handling
            if ts_ascat is None:
                print 'No ascat data for gpi %0i' % gpi
                ts_ascat = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_ascat = ts_ascat[ts_ascat.flag ==
                                    0]['sm'][start_date:end_date]
            # append to data_group
            ts_ascat.index = ts_ascat.index.date
            data_group['ascat'] = ts_ascat

        if 'ascat_reckless_rom' in satellites:
            ts_ascat_reckless_rom = self.ascat_reckless_rom.read(lon, lat)
            if ts_ascat_reckless_rom is None:
                print 'No veg_corr ascat data for gpi %0i' % gpi
                ts_ascat_reckless_rom = pd.Series(
                    index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_ascat_reckless_rom = ts_ascat_reckless_rom[(
                    ts_ascat_reckless_rom['proc_flag'] <= 2) &
                    (ts_ascat_reckless_rom['ssf'] == 1)]['sm']
                # drop hours, mins, secs
                ts_ascat_reckless_rom.index = ts_ascat_reckless_rom.index.normalize()
            # append to data group
            ts_ascat_reckless_rom = ts_ascat_reckless_rom.resample('D').mean()
            data_group['ascat_reckless_rom'] = ts_ascat_reckless_rom

        if 'amsr2' in satellites:
            # read amsr2 data
            ts_amsr2 = self.amsr2.read(lon, lat)
            # error handling
            if ts_amsr2 is None:
                print 'No amsr2 data for gpi %0i' % gpi
                ts_amsr2 = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_amsr2 = ts_amsr2[ts_amsr2.flag ==
                                    0]['sm'][start_date:end_date]
            # append to data_group
            ts_amsr2.index = ts_amsr2.index.date
            data_group['amsr2'] = ts_amsr2

        if 'smap' in satellites:
            # read amsr2 data
            ts_smap = self.smap.read(lon, lat)
            # error handling
            if ts_smap is None:
                print 'No smap data for gpi %0i' % gpi
                ts_smap = pd.Series(
                    index=pd.date_range(
                        start=start_date,
                        end=end_date))
            else:
                ts_smap = ts_smap['soil_moisture'][start_date:end_date]
            # append to data_group
                ts_smap.index = ts_smap.index.date
            data_group['smap'] = ts_smap * 100

        return data_group


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.style.use('ggplot')

    from irrigation.prep import interp, smooth
    from pytesmo import scaling

    gpi = 726000

    data = QDEGdata()
    ts = data.read_gpi(gpi, '2007-01-01', '2016-12-31',
                       models=['merra'],
                       satellites=['ascat_reckless_rom',
                                   #'amsr2',
                                   #'smap',
                                   ])

    ts.dropna(inplace=True)
    ts_scaled = scaling.scale(ts, 'mean_std', 0)
    ts_scaled = ts_scaled.divide(100)
    ts_smooth = smooth.iter_movav(ts_scaled, 35)

    ax = ts_scaled.plot(title=str(gpi))  # , ylim=(0,1))
    ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax.set_xlabel('Datetime')

    ax2 = ts_smooth.plot(title=str(gpi))  # , ylim=(0, 1))
    ax2.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax2.set_xlabel('Datetime')
    plt.show()
