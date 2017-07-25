import pandas as pd

from pytesmo import scaling

from irrigation.inout import importdata
from irrigation.prep import interp, smooth

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')


def prepare(gpi, start_date, end_date, model, satellites, kind="clim"):
    """
    Prepare eraland, amsre, ascat, amsr2 time series for processing. First apply gapfilling,
    then calculate climatology or moving average as specified by kind and lastly
    scale satellite data to the model data.

    :param gpi: int
        gpi in qdeg grid
    :param start_date: string
        start date
    :param end_date: string
        end date
    :param kind: "clim", "movav"
        if "clim", yield climatology of ts (0-366 days)
        if "movav" yield smoothed ts from start_date to end_date
    :param plot: Boolean
        if True show plot for each step
    :return: pd.DataFrame
        all input ts with pre-processing steps applied
    """
    # read data
    data_object = importdata.QDEGdata()
    # TODO: resolve problems concerning data overlap periods, specifically amsr2
    ts_input = data_object.read_gpi(gpi, start_date, end_date, model, satellites)

    # gapfill
    ts_gapfill = interp.iter_fill(ts_input, 7)

    # smooth
    if kind == 'clim':
        ts_smooth = smooth.iter_climats(ts_gapfill)
        plot_title = 'Climatology'
    elif kind == 'movav':
        ts_smooth = smooth.iter_movav(ts_gapfill, 35)
        plot_title = 'Moving average'
    else:
        plot_title = ''
        raise Exception(
            "Wrong input, specify 'clim' or 'movav'.")

    # drop rows with missing values
    ts_smooth = ts_smooth.dropna()
    # scale sats to model
    ts_scaled = scaling.scale(ts_smooth, 'mean_std', 0)
    return ts_scaled


def plot_ts(gpi, start_date, end_date, kind="clim", plot=True):
    """
    Prepare eraland, amsre, ascat, amsr2 time series for processing. First apply gapfilling,
    then calculate climatology or moving average as specified by kind and lastly
    scale satellite data to the model data.

    :param gpi: int
        gpi in qdeg grid
    :param start_date: string
        start date
    :param end_date: string
        end date
    :param kind: "clim", "movav"
        if "clim", yield climatology of ts (0-366 days)
        if "movav" yield smoothed ts from start_date to end_date
    :param plot: Boolean
        if True show plot for each step
    :return: pd.DataFrame
        all input ts with pre-processing steps applied
    """
    # read data
    data_object = importdata.QDEGdata()
    ts_input = data_object.read_gpi_old(gpi, start_date, end_date, 'eraland', 'ascat', 'amsre')

    # gapfill
    ts_gapfill = interp.iter_fill(ts_input, 7)
    # drop rows with nan values
    ts_gapfill = ts_gapfill.dropna(thresh=3)

    # smooth
    if kind == 'clim':
        ts_smooth = smooth.iter_climats(ts_gapfill)
        plot_title = 'Climatology'
    elif kind == 'movav':
        ts_smooth = smooth.iter_movav(ts_gapfill, 35)
        plot_title = 'Moving average'
    else:
        plot_title = ''
        raise Exception(
            "Wrong input, specify 'clim' or 'movav'.")

    # scale sats to model
    ts_scaled = scaling.scale(ts_smooth, 'mean_std', 0)

    if plot:

        # gpi location info
        lon, lat = importdata.qdeg2lonlat(gpi)
        location = " (lon: {}, lat: {})".format(lon, lat)
        print location
        xlabel = "Time"
        ylabel = "Surface soil moisture (%)"

        # input ts data
        ax = ts_input.plot(title="Input timeseries" + location, ylim=[0, 100])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.legend(loc='upper left')
        plt.tight_layout()
        """
        # gap filled
        ax = ts_gapfill.plot(title="Gap-filled timeseries", ylim=[0, 100])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.legend(loc='lower left')
        plt.tight_layout()
        # smoothed
        ax = ts_smooth.plot(title=plot_title, ylim=[0, 100])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.legend(loc='lower left')
        plt.tight_layout()
        """
        # scaled
        ax = ts_scaled.plot(title=plot_title+" (Scaled)")
        #sns.despine()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.legend(loc='upper left')
        plt.tight_layout()

        plt.show()

    return ts_scaled


if __name__ == "__main__":
    # test func
    # 721798 is mississippi example gpi
    # 696362 egypt
    gpi = 750568
    ts = prepare(gpi=gpi,
            start_date='2015-01-01',
            end_date='2016-12-31',
            model='merra',
                 # ['ascat','ascat_ultimate_uhnari', 'amsr2','smap']
            satellites=['ascat','ascat_ultimate_uhnari', 'amsr2','smap'],
            kind='movav')
    print ts

    #title = 'ERA-Interim/Land reanalysis product (gpi={})'.format(str(gpi))
    #title = 'GLDAS NOAH v2.1 (gpi={})'.format(str(gpi))
    title = 'MERRA2 (gpi={})'.format(str(gpi))
    ax = ts.plot(title=title)
    ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax.set_xlabel(r"Time")

    plt.show()
