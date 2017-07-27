# -*- coding: utf-8 -*-

import os
import pandas as pd
from rsroot import root_path

# GLDAS
from gldas.interface import GLDASTs
# ERALAND
from rsdata.ECMWF.interface import ERALAND_g2ze
# MERRA
from irrigation.inout.merra.interface import MERRA2_Ts
# CCI reader
from smecv.input.common_format import CCIDs
# ASCAT versions
from pynetcf.time_series import GriddedNcContiguousRaggedTs
# SMAP
from smap_io.interface import SMAPTs
# QDEG to lon lat conversion
from pygeogrids.grids import genreg_grid
import pygeogrids.netcdf as ncgrids

qdeg_grid = genreg_grid(grd_spc_lat=0.25, grd_spc_lon=0.25).to_cell_grid()

# TODO: find better solution for ascat reader
# generate warp grid
warp_grid_path = '/home/fzaussin/shares/radar/Datapool_processed/WARP/ancillary/warp5_grid/TUW_WARP5_grid_info_2_1.nc'
warp_grid = ncgrids.load_grid(warp_grid_path)
# version reckless rom
warp_path_reckless_rom = '/home/fzaussin/shares/radar/Datapool_processed/WARP/datasets/reckless_rom/R1AB/080_ssm/netcdf'
io_ascat_reckless_rom = GriddedNcContiguousRaggedTs(path=warp_path_reckless_rom, grid=warp_grid)
# version ultimate uhnari -> dynamic slope recommended by sebhahn
warp_path_ultimate_uhnari = '/home/fzaussin/shares/radar/Datapool_processed/WARP/datasets/ultimate_uhnari/R1A/080_ssm/netcdf/'
io_ascat_ultimate_uhnari = GriddedNcContiguousRaggedTs(path=warp_path_ultimate_uhnari, grid=warp_grid)



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

def merra2_ts(gpi):
    ts_path2 = os.path.join(root_path.r,
                            'Datapool_processed',
                            'Earth2Observe',
                            'MERRA2',
                            'M2T1NXLND.5.12.4',
                            'datasets',
                            'ts_hourly_means_part2')
    merra = MERRA2_Ts(ts_path=ts_path2)
    lon, lat = qdeg2lonlat(gpi)
    ts = merra.read(lon, lat)
    # resample to daily means
    return ts.resample('D').mean()

def ascat_reckless_rom(gpi):
    """Read ascat data with new vegetation correction"""
    lon, lat = qdeg2lonlat(gpi)
    ascat_ts = io_ascat_reckless_rom.read(lon, lat)
    return ascat_ts

def ascat_ultimate_uhnari(gpi):
    """Read ascat data with new vegetation correction"""
    lon, lat = qdeg2lonlat(gpi)
    ascat_ts = io_ascat_ultimate_uhnari.read(lon, lat)
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

    def read_gpi(self, gpi, start_date, end_date, model=None, satellites=None):
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
            ts_gldas = GLDASTs(ts_path='/home/fzaussin/shares/radar/Datapool_processed/GLDAS/GLDAS_NOAH025_3H.2.1/datasets/').read(gpi)
            # error handling
            if ts_gldas is None:
                print 'No gldas data for gpi %0i' % gpi
                ts_gldas = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_gldas = ts_gldas[start_date:end_date]
                # append to data_group
            data_group['gldas'] = ts_gldas['SoilMoi0_10cm_inst']

        elif model == 'merra':
            ts_merra = merra2_ts(gpi)
            # error handling
            if ts_merra is None:
                print 'No merra data for gpi %0i' % gpi
                ts_merra = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_merra = ts_merra[start_date:end_date]
                # append to data_group
            data_group['merra'] = ts_merra['GWETTOP'] * 100
        elif model == None:
            pass
        else:
            raise NotImplementedError
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

        if 'ascat_reckless_rom' in satellites:
            ts_ascat_reckless_rom = ascat_reckless_rom(gpi)
            if ts_ascat_reckless_rom is None:
                print 'No veg_corr ascat data for gpi %0i' % gpi
                ts_ascat_reckless_rom = pd.Series(
                    index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_ascat_reckless_rom = ts_ascat_reckless_rom[(ts_ascat_reckless_rom['proc_flag'] <= 2) & (ts_ascat_reckless_rom['ssf'] == 1)][
                    'sm']
                # drop hours, mins, secs
                ts_ascat_reckless_rom.index = ts_ascat_reckless_rom.index.normalize()
            # append to data group
            #ts_ascat_reckless_rom.index = ts_ascat_reckless_rom.index.date
            ts_ascat_reckless_rom = ts_ascat_reckless_rom.resample('D').mean()
            data_group['ascat_reckless_rom'] = ts_ascat_reckless_rom

        if 'ascat_ultimate_uhnari' in satellites:
            ts_ascat_ultimate_uhnari = ascat_ultimate_uhnari(gpi)
            if ts_ascat_ultimate_uhnari is None:
                print 'No veg_corr ascat data for gpi %0i' % gpi
                ts_ascat_reckless_rom = pd.Series(
                    index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_ascat_ultimate_uhnari = ts_ascat_ultimate_uhnari[(ts_ascat_ultimate_uhnari['proc_flag'] <= 2) & (ts_ascat_ultimate_uhnari['ssf'] == 1)][
                    'sm']
                # drop hours, mins, secs
                ts_ascat_ultimate_uhnari.index = ts_ascat_ultimate_uhnari.index.normalize()
            # append to data group
            #ts_ascat_reckless_rom.index = ts_ascat_reckless_rom.index.date
                ts_ascat_ultimate_uhnari = ts_ascat_ultimate_uhnari.resample('D').mean()
            data_group['ascat_ultimate_uhnari'] = ts_ascat_ultimate_uhnari

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

        if 'smap' in satellites:
            # read amsr2 data
            lon, lat = qdeg2lonlat(gpi)
            ts_smap = SMAPTs('/home/fzaussin/SMAP_L3_P_v3').read(lon, lat)
            # error handling
            if ts_smap is None:
                print 'No smap data for gpi %0i' % gpi
                ts_smap = pd.Series(index=pd.date_range(start=start_date, end=end_date))
            else:
                ts_smap = ts_smap['soil_moisture'][start_date:end_date]
            # append to data_group
                ts_smap.index=ts_smap.index.date
            data_group['smap'] = ts_smap * 100

        return data_group

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.style.use('ggplot')

    # TODO: temp to compare smap and merra nicely in plots
    from irrigation.prep import interp, smooth
    from pytesmo import scaling

    gpi = 726000

    data = QDEGdata()
    ts_test = data.read_gpi(gpi, '2007-01-01', '2016-12-31',
                                 model='merra',
                                 satellites=[#'ascat',
                                             'ascat_reckless_rom',
                                             #'ascat_ultimate_uhnari',
                                             #'amsr2',
                                             #'amsre',
                                             #'smap'
                                 ])
    # TODO: see first TODO
    ts_test.dropna(inplace=True)
    ts_scaled = scaling.scale(ts_test, 'mean_std', 0)
    ts_scaled = ts_scaled.divide(100)
    ts_smooth = smooth.iter_movav(ts_scaled, 35)

    ax = ts_scaled.plot(title=str(gpi))#, ylim=(0,1))
    ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax.set_xlabel('Datetime')

    ax2 = ts_smooth.plot(title=str(gpi))#, ylim=(0, 1))
    ax2.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax2.set_xlabel('Datetime')
    plt.show()

