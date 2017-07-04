from irrigation.inout import importdata
from irrigation.prep import interp, smooth

import matplotlib.pyplot as plt
from pytesmo import scaling

import numpy as np
import pandas as pd


def prepare_ts(gpi, start_date, end_date):
    """"""
    # read ts
    data_object = importdata.QDEGdata()
    ts = data_object.read_gpi(gpi, start_date, end_date, 'gldas', 'ascat', 'amsre')
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

    gpi = 726120
    start_date = '2007-01-01'
    end_date = '2013-12-31'

    df = prepare_ts(gpi, start_date, end_date)
    df.plot()

    #df_irrig = irrig_increments(gpi,start_date, end_date, resampling='Q-NOV')
    #df_irrig.plot()
    plt.show()
