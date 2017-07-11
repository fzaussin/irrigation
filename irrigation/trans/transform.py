import numpy as np
import pandas as pd

def calc_gaps(df):
    """ appends a column to a df with datetime index indicating data gaps in days"""
    df_gaps = df.copy()
    df_gaps['date'] = df_gaps.index.values
    df_gaps['gaps'] = df_gaps.date.shift(1) - df_gaps.date
    df_gaps['gaps'] = df_gaps.gaps / np.timedelta64(1, 'D')
    df_gaps.drop('date', axis=1, inplace=True)
    return df_gaps

def shift_diff(df, shift=1):
    """calc diff between df and df shifted by x days"""
    df_copy = df.copy()
    # bit dirty, initially holds dates, then the date gaps in days
    df_copy['datagap'] = df.index.values
    # (y_i - y_i-x) for each column
    df_slopes = df_copy - df_copy.shift(shift)
    df_slopes['datagap'] = df_slopes['datagap'] / np.timedelta64(1,'D')
    return df_slopes

