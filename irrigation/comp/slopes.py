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

def diffquot_slope(df, ref_col='datagap'):
    """
    Calculate slope by means of a differential quotient, e.g.
    (y2-y1)/(x2-x1)
    """
    # calculate changes between observations
    daily_diffs = transform.shift_diff(df, shift=1)
    # calc diff qoutient by dividing each ts through the data gap
    datagaps = daily_diffs[ref_col].values
    daily_diffs = daily_diffs.drop(ref_col, axis=1)
    # init empty df
    df_slopes = pd.DataFrame(index=df.index)
    for series in daily_diffs:
        # divide changes in y by changes in x -> local slopes
        # TODO: data gap is always 1, because we don't drop any rows: need to calculate per sensor

        df_slopes[series] = np.divide(daily_diffs[series], datagaps)
    return df_slopes

def diffquot_slope_test(df):
    """
    Same as above but without dividing by data gap. Large lags therefore are
    not underweighted. -> just y2-y1
    :param df:
    :return:
    """
    # calculate changes between observations
    daily_diffs = transform.shift_diff(df, shift=1)
    # calc diff qoutient by dividing each ts through the data gap
    daily_diffs = daily_diffs.drop('datagap', axis=1)
    return daily_diffs

def diffquot_slope_climat(df):
    """
    for climat y2-y1 is always 1 yielding a simple subtraction from
    day x to x+1
    """
    return df - df.shift(1)

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
    model_slopes = df[df.columns.values[reference_index]]
    df = df.drop([df.columns.values[reference_index]], axis=1)

    # satellite - model slope element wise
    for series in df:
        slope_diffs = np.subtract(df[series].values, model_slopes.values)
        #pos_slope_diffs = slope_diffs[slope_diffs > 0]
        df[series] = pd.Series(
            slope_diffs,
            index=df.index)
    # return only positive values
    return df[df>0]

def aggregate_psds(df, resampling='Q-NOV'):
    """Calculate aggregated sum"""
    return df.resample(resampling).sum()


def slope_metric_italians(df, resampling='Q-NOV', reference_index=0):
    """
    Implemenation of the slopes approach of the italians.
    Counts events where dsm_sat > dsm_mod if:
    dsm_sat > 0 & dsm_mod <= 0
    Takes model and satellite slopes as input!
    :param satellite_slopes:
    :param ref_idx:
    :return:
    """
    # split into model and satellite data
    model_slopes = df[df.columns.values[reference_index]]
    satellite_slopes = df.drop([df.columns.values[reference_index]], axis=1)

    # mask out if model slope is positive (rainfall event)
    # mask out if satellite slope is not positive
    model_slopes[model_slopes > 0] = np.nan
    satellite_slopes[satellite_slopes <= 0] = np.nan

    # satellite - model slope for each day
    for series in satellite_slopes:
        slope_diffs = np.subtract(satellite_slopes[series].values, model_slopes.values)
        satellite_slopes[series] = pd.Series(
            slope_diffs,
            index=satellite_slopes.index)
    # restrict to dsm_sat > dsm_mod
    pos_slope_diff = satellite_slopes[satellite_slopes > 0]
    # count events (eg non nan values in the resampled period)
    return pos_slope_diff.resample('Q-NOV').count()

def new_slope_metric(df, reference_index=0):
    """
    Implemenation of the slopes approach of the italians. Modified to return the
    satellite SM increments through irrigation instead of event counts.

    Counts events where dsm_sat > dsm_mod if:
    dsm_sat > 0 & dsm_mod <= 0
    Takes model and satellite slopes as input!
    :param satellite_slopes:
    :param ref_idx:
    :return:
    """
    # split into model and satellite data
    model_slopes = df[df.columns.values[reference_index]]
    satellite_slopes = df.drop([df.columns.values[reference_index]], axis=1)

    # mask out if model slope is positive (rainfall event)
    # mask out if satellite slope is not positive
    model_slopes[model_slopes > 0] = np.nan
    satellite_slopes[satellite_slopes <= 0] = np.nan

    # satellite - model slope for each day
    for series in satellite_slopes:
        slope_diffs = np.subtract(satellite_slopes[series].values, model_slopes.values)
        satellite_slopes[series] = pd.Series(
            slope_diffs,
            index=satellite_slopes.index)
    # restrict to dsm_sat > dsm_mod
    pos_slope_diff = satellite_slopes[satellite_slopes > 0]
    return pos_slope_diff



if __name__=='__main__':
    import time
    import datetime
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.style.use('ggplot')
    from irrigation.prep import timeseries, interp
    from irrigation.trans.transform import qdeg2lonlat

    gpi = 760668
    location = ''

    ts = timeseries.prepare(gpi=gpi,
                            start_date='2012-01-01',
                            end_date='2016-12-31',
                            models=['merra'],
                            satellites=['smapv4',
                                        'ascatrecklessrom',
                                        'amsr2',
                                        #'smap'
                                        ],
                            kind='clim',
                            window=35)
    ax1 = ts.plot()
    ax1.set_ylabel(r"Soil moisture ($m^{3} m^{-3}$)")
    ax1.set_xlabel('Datetime')
    # calc psd
    slopes_climat = diffquot_slope_climat(ts)
    pos_slope_diffs = psd(slopes_climat)

    #res = pos_slope_diffs.resample('M').sum()
    print pos_slope_diffs

    ax2 = pos_slope_diffs.plot.area(title=str(gpi))
    ax2.set_ylabel(r'$SM^{+}_{Irr}$ ($m^{3}m^{-3}$)')
    ax2.set_xlabel('Datetime')
    plt.show()
