import numpy as np
import pandas as pd

from datetime import timedelta
from irrigation.trans import transform


def slopes_movav(df):
    """"""
    # calculate slope using 1st and 3rd, then 2nd and 4th value
    window = [-1, 0, 1]
    # calc gaps in ts data for increments in days between data points
    df_gaps = transform.calc_gaps(df)
    x = df_gaps.gaps.values
    # init container
    df_slopes = pd.DataFrame(index=df.index)
    for series in df.columns:
        # iterate df and calc slopes for each col
        slopes_y = np.convolve(df[series], window, mode='same')
        #slopes_x = np.convolve(x, window, mode='same')
        # TODO: 8UNG, x is only the length of the data gap in days and no 'movav' increment! -> SOLUTION?
        df_slopes[series] = np.divide(slopes_y,
                                      x)
    return df_slopes

def slopes_climat(df):
    """operates only on climat"""
    # calculate slope using 1st and 3rd, then 2nd and 4th value
    window = [-1, 0, 1]
    x = df.index.values
    df_slopes = pd.DataFrame(index=df.index)
    for series in df.columns:
        slopes_y = np.convolve(df[series], window, mode='same')
        slopes_x = np.convolve(x, window, mode='same')
        df_slopes[series] = np.divide(slopes_y,
                                      slopes_x)
    return df_slopes

def psd(df, reference_index = 0):
    """"""
    model_data = df[df.columns.values[reference_index]]
    df = df.drop([df.columns.values[reference_index]], axis=1)
    # satellite - model slope element wise
    for series in df:
        slope_diffs = np.subtract(df[series].values, model_data.values)
        #pos_slope_diffs = slope_diffs[slope_diffs > 0]
        df[series] = pd.Series(
            slope_diffs,
            index=df.index)
    # return only positive values
    return df[df>0]

def psds(df, start=0, end=366):
    """"""
    # TODO: temp function to test JJA psds
    # return series object
    return df[start:end].sum()

def aggregate_psds(df, resampling='Q-NOV'):
    """Calculate aggregated sum"""
    return df.resample(resampling).sum()


if __name__=='__main__':
    import time
    import datetime
    import matplotlib.pyplot as plt
    from irrigation.prep import timeseries

    gpi = 696365
    df = timeseries.prepare(gpi=gpi,
                            start_date='2007-01-01',
                            end_date='2011-12-31',
                            kind='movav')
    df.plot()
    # aggregate psds
    df_slopes = slopes_movav(df)
    df_psd = psd(df_slopes)
    #seasonal = aggregate_psds(df_psd, 'Q-NOV')
    #seasonal.plot(kind='bar')

    plt.show()
