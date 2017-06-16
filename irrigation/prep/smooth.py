import numpy as np
import pandas as pd

from pytesmo.time_series import anomaly
from pytesmo.time_series.filtering import moving_average


def iter_climats(df):
    """"""
    df_gapfill = pd.DataFrame(index=np.arange(1,367))
    for series in df.columns:
        df_gapfill[series] = anomaly.calc_climatology(df[series])
    return df_gapfill


def iter_movav(df, window_size=1):
    """"""
    df_movav = pd.DataFrame(index=df.index)
    for series in df.columns:
        df_movav[series] = moving_average(df[series], window_size=window_size)
    return df_movav
