from pynetcf.time_series import GriddedNcContiguousRaggedTs
from rsdata.TRMM_TMPA.interface import Tmpa3B42Ts
import pygeogrids.netcdf as ncgrids
import numpy as np



path_warp_grid = ncgrids.load_grid('/home/fzaussin/data/GRIDS/TUW_WARP5_grid_info_2_1.nc')
path_ascat_reckless_rom = '/home/fzaussin/data/WARP/reckless_rom'

ascat = GriddedNcContiguousRaggedTs(
            path=path_ascat_reckless_rom, grid=path_warp_grid)

def read_ascat(lon, lat):
    ts = ascat.read(lon, lat)

    ts = ts[(ts['proc_flag'] <= 2) & (ts['ssf'] == 1)]['sm']
    # drop hours, mins, secs
    ts.index = ts.index.normalize()
    ts = ts.resample('D').mean()
    return ts

def trmm_reader(lon, lat):
    """read 6 hourly trmm data"""
    trmm = Tmpa3B42Ts()
    trmm_data = trmm.read_ts(lon, lat)
    # set outliers to nan
    trmm_data.loc[trmm_data['pcp'] == -9999.900391] = np.nan
    pcp = trmm_data['pcp']
    return pcp.resample('D').sum()


if __name__=='__main__':
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.style.use('ggplot')

    lon, lat = -118.523552, 47.159946

    ascat = read_ascat(lon, lat)['2008-01-01':'2014-12-31']
    trmm = trmm_reader(lon, lat)['2008-01-01':'2014-12-31']

    #ratio = ascat.resample('Q-NOV').sum() / trmm.resample('Q-NOV').sum()
    #print ratio

    ax = ascat.plot()
    trmm.plot(ax=ax)

    #ratio.plot()


    plt.show()