# -*- coding: utf-8 -*-
import numpy as np
from pytesmo import scaling

from irrigation.inout import importdata
from irrigation.prep import interp, smooth

# init data object
data_object = importdata.QDEGdata()

def prepare(gpi, start_date, end_date, models, satellites, kind="clim"):
    """
    Prepare eraland, amsre, ascat, amsr2 time series for processing. First drop nan values,
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
    ts_input = data_object.read_gpi(gpi, start_date, end_date, models, satellites)
    ts_gapfill = interp.iter_fill(ts_input, max_gap=5)

    # either calc climatology, apply moving average filter, or do nothing
    if kind == 'clim':
        ts_smooth = smooth.iter_climats(ts_gapfill)
        plot_title = 'Climatology'
    elif kind == 'movav':
        ts_smooth = smooth.iter_movav(ts_gapfill, 35)
        plot_title = 'Moving average'
    elif kind == None:
        # return original data
        ts_smooth = ts_gapfill
    else:
        raise NotImplementedError
        pass

    # drop rows with missing values
    ts_smooth = ts_smooth.dropna()
    # scale satellite data to model data
    ts_scaled = scaling.scale(ts_smooth, 'mean_std', 0)
    return ts_scaled


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.style.use('ggplot')

    # test
    gpi = 726120

    ts = prepare(gpi=gpi,
            start_date='2007-01-01',
            end_date='2016-12-31',
            models=['merra'],
            satellites=['ascat_reckless_rom'],
            kind='clim')
    print ts
    title = 'Gpi #{}'.format(str(gpi))
    ax = ts.plot(title=title)
    ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax.set_xlabel(r"Time")

    plt.show()
