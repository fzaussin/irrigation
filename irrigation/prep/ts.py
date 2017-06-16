import pandas as pd

from pytesmo import scaling

from irrigation.inout import import_data
from irrigation.prep import interp, smooth

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white", context='paper', palette=sns.diverging_palette(220, 20, s=80, l=40))


def prepare_ts(gpi, start_date, end_date, kind="clim", plot=False):
    """
    Prepare input ts (eraland, amsre, ascat, amsr2) for processing. First apply gapfilling,
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
    data_object = import_data.QDEGdata()
    ts_input = data_object.read_gpi(gpi, start_date, end_date, 'eraland', 'amsre', 'ascat')

    # gapfill
    ts_gapfill = interp.iter_fill(ts_input, 10)

    # smooth
    if kind == 'clim':
        ts_smooth = smooth.iter_climats(ts_gapfill)
        plot_title = 'Climatology'
    elif kind == 'movav':
        ts_smooth_temp = smooth.iter_movav(ts_gapfill, 35)
        # drop rows with nan values
        ts_smooth = ts_smooth_temp.dropna()
        plot_title = 'Moving average'
    else:
        plot_title = ''
        raise Exception(
            "Wrong input, specify 'clim' or 'movav'.")

    # scale sats to model
    ts_scaled = scaling.scale(ts_smooth, 'mean_std', 0)

    if plot:

        # gpi location info
        lon, lat = import_data.qdeg2lonlat(gpi)
        location = " (lon: {}, lat: {})".format(lon, lat)

        # input ts data
        ax = ts_input.plot(title="Input timeseries" + location, ylim=[0, 100])
        ax.set_xlabel("Time [days]")
        ax.set_ylabel("SSM [%]")
        # gap filled
        ax = ts_gapfill.plot(title="Gap-filled timeseries", ylim=[0, 100])
        ax.set_xlabel("Time [days]")
        ax.set_ylabel("SSM [%]")
        # smoothed
        ax = ts_smooth.plot(title=plot_title, ylim=[0, 100])
        ax.set_xlabel("Time [days]")
        ax.set_ylabel("SSM [%]")

        ax = ts_scaled.plot(title=plot_title + ' (Scaled)', ylim=[0, 100])
        ax.set_xlabel("Time [days]")
        ax.set_ylabel("SSM [%]")

        plt.show()

    return ts_scaled


if __name__ == "__main__":
    # test func
    prepare_ts(gpi=726003,
               start_date='2002-01-01',
               end_date='2012-12-31',
               kind='movav',
               plot=True)
