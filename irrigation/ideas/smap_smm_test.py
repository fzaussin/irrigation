from irrigation.inout import importdata
from irrigation.prep import interp

import matplotlib.pyplot as plt
from pytesmo import scaling

import numpy as np
import pandas as pd


def prepare_ts(gpi, start_date, end_date):
    """"""
    # read ts
    data_object = importdata.QDEGdata()
    ts = data_object.read_gpi_old(gpi, start_date, end_date, 'eraland', 'ascat', 'amsre')
    # gapfill
    ts_gapfill = interp.iter_fill(ts, 5)
    ts_gapfill = ts_gapfill.dropna()
    # scaling
    ts_scaled = scaling.scale(ts_gapfill, 'mean_std', 0)
    return ts_scaled

def pos_deltas(ts_scaled):
    # shift one day
    ts_copy = ts_scaled.copy()
    timedelta = pd.Timedelta('1 days')
    ts_copy_shift1 = ts_copy.shift(1, timedelta)
    # daily changes
    deltas = ts_copy - ts_copy_shift1
    # positive daily changes
    pos_deltas = deltas[deltas > 0]
    return pos_deltas

def calc_irrig(pos_deltas, resampling='M'):
    """"""
    # TODO: difference of resampling before and after subtracting sat - model ??
    # resample positive increments
    print pos_deltas
    resampled_deltas = pos_deltas.resample(resampling).sum()
    print resampled_deltas
    # sat - mod
    reference_index = 0
    model = resampled_deltas[resampled_deltas.columns.values[reference_index]]
    df_irrigation = resampled_deltas.drop([resampled_deltas.columns.values[reference_index]], axis=1)
    for series in df_irrigation:
        # satellite - model deltas
        irrigation = np.subtract(df_irrigation[series].values, model.values)
        df_irrigation[series] = pd.Series(
            irrigation,
            index=df_irrigation.index)

    irrig = df_irrigation.resample(resampling).sum()
    return irrig


def irrig_increments(gpi, start_date, end_date, resampling='Q-NOV'):
    """"""
    ts_scaled = prepare_ts(gpi, start_date, end_date)
    deltas = pos_deltas(ts_scaled)
    irrig = calc_irrig(deltas, resampling)
    return irrig


def iterate_gpis(gpi_list):
    """"""


if __name__=='__main__':
    # process for us
    import time
    import datetime

    # set date range
    start_date = '2007-01-01'
    end_date = '2011-12-31'

    # init output containers
    df_ascat = pd.DataFrame()
    df_amsre = pd.DataFrame()

    # path to gpis
    path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
    gpis_lcmask = pd.DataFrame.from_csv(path)
    gpis = gpis_lcmask['gpi_quarter']
    gpis = gpis.sort_values()

    tic = time.clock()
    for gpi in gpis:
        try:
            df_irrig = irrig_increments(gpi, start_date, end_date,
                                        resampling='Q-NOV')
            print df_irrig
            df_ascat[str(gpi)] = df_irrig['ascat']
            df_amsre[str(gpi)] = df_irrig['amsre']

        except (ValueError, IOError, RuntimeError):
            df_ascat[str(gpi)] = np.nan
            df_amsre[str(gpi)] = np.nan

    # transpose
    df_ascat_out = df_ascat.transpose()
    df_amsre_out = df_amsre.transpose()
    # save to csv
    df_ascat_out.to_csv(
        '/home/fzaussin/Desktop/US-pos-increments-ascat.csv')
    df_amsre_out.to_csv(
        '/home/fzaussin/Desktop/US-pos-increments-amsre.csv')

    toc = time.clock()
    print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))

    """ SIMPLE PLOT
    gpi = 743746
    start_date = '2007-01-01'
    end_date = '2013-12-31'

    df = prepare_ts(gpi, start_date, end_date)
    df.plot(title='input ts')

    df_irrig = irrig_increments(gpi,start_date, end_date, resampling='Q-NOV')
    df_irrig.plot(kind='bar', title='positive sm increments')
    plt.show()
    """
