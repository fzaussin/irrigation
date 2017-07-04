import numpy as np
import pandas as pd

def calc_gaps(df):
    """ appends a column to a df with datetime index indicating data gaps in days"""
    df_gaps = df.copy()
    df_gaps['date'] = df_gaps.index.values
    df_gaps['gaps'] = df_gaps.date.shift(1) - df_gaps.date
    df_gaps['gaps'] = df_gaps.gaps / np.timedelta64(1, 'D')
    return df_gaps