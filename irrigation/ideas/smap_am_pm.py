import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pygeogrids.grids import genreg_grid
from smap_io.interface import SMAPTs

qdeg_grid = genreg_grid(grd_spc_lat=0.25, grd_spc_lon=0.25).to_cell_grid()

# init smap readers
path_am = '/home/fzaussin/data/SPL3SMP_v4/AM_descending'
path_pm = '/home/fzaussin/data/SPL3SMP_v4/PM_ascending'

smap_am = SMAPTs(path_am)
smap_pm = SMAPTs(path_pm)


class smap_data(object):
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

        path_smap_v4_am = '/home/fzaussin/data/SPL3SMP_v4/AM_descending'
        path_smap_v4_pm = '/home/fzaussin/data/SPL3SMP_v4/PM_ascending'

        # init data objects
        self.qdeg_grid = genreg_grid(
            grd_spc_lat=0.25,
            grd_spc_lon=0.25).to_cell_grid()


        self.smap_v4_am = SMAPTs(path_smap_v4_am)
        self.smap_v4_pm = SMAPTs(path_smap_v4_pm)


    def qdeg2lonlat(self, gpi):
        """
        Return lon and lat for a given 0.25 grid point index
        :param gpi:
        :return: lon, lat
        """
        lon, lat = self.qdeg_grid.gpi2lonlat(gpi)
        return lon, lat * (-1)

    def read_gpi(self, gpi):
        """"""
        lon, lat = self.qdeg2lonlat(gpi)
        smap_am = self.smap_v4_am.read(lon, lat)['soil_moisture']
        smap_pm = self.smap_v4_pm.read(lon, lat)['soil_moisture_pm']
        return pd.concat([smap_am, smap_pm], axis=1)

    def read_1d(self, gpi):
        """add 6am and 6pm to corresponding timestamps to merge
        asc and desc orbits"""
        lon, lat = self.qdeg2lonlat(gpi)
        smap_am = self.smap_v4_am.read(lon, lat)['soil_moisture']
        smap_pm = self.smap_v4_pm.read(lon, lat)['soil_moisture_pm']
        # add hours
        smap_am.index = smap_am.index + pd.DateOffset(hours=6)
        smap_pm.index = smap_pm.index + pd.DateOffset(hours=18)
        return pd.concat([smap_am, smap_pm], axis=0).sort_index()


def day_night_diff(ts, resampling='Q-NOV'):
    """
    sm diff between morning of day x and evening of day x-1,
    then sums up the differences. kind of a measure for sm
    variability.
    """
    day_night_diff = ts['soil_moisture'] - ts['soil_moisture_pm'].shift(1)
    agg_diff = day_night_diff.resample(resampling).sum()
    return agg_diff


if __name__=="__main__":
    from prep import interp
    gpi = 750568

    reader = smap_data()
    ts = reader.read_1d(gpi)
    roll_mean = ts.dropna().rolling(window=35).mean()
    roll_mean.plot()
    # print corr['soil_moisture']['soil_moisture_pm']

    #agg_diff = day_night_diff(ts, resampling='M')
    #agg_diff.plot(title=str(gpi))
    #print agg_diff

    ts.plot(style='.-', title=str(gpi))
    plt.show()