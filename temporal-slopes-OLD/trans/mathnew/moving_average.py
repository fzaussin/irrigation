# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 14:43:58 2015

@author: agruber
"""

import pandas as pd
from datetime import timedelta
import numpy as np

def moving_average(data, window_size='1d', min_periods=1, center=True):
    ''' Function that computes a rolling mean

    Parameters
    ----------
    data : DataFrame or Series
           If a DataFrame is passed, the rolling_mean is computed for all columns.
    window : int or string
             If int is passed, window is the number of observations used for calculating 
             the statistic, as defined by the function pd.rolling_mean()
             If a string is passed, it must be a frequency string, e.g. '90S'. This is
             internally converted into a DateOffset object, representing the window size.
    min_periods : int
                  Minimum number of observations in window required to have a value.

    Returns
    -------
    Series or DataFrame, if more than one column    
    '''
    def f(x):
        '''Function to apply that actually computes the rolling mean'''
        if center == False:
            dslice = col[x-pd.datetools.to_offset(window_size).delta+timedelta(0,0,1):x]
                # adding a microsecond because when slicing with labels start and endpoint
                # are inclusive
        else:
            dslice = col[x-pd.datetools.to_offset(window_size).delta/2+timedelta(0,0,1):
                         x+pd.datetools.to_offset(window_size).delta/2]
        if dslice.size < min_periods:
            return np.nan
        else:
            return dslice.mean()

    data = pd.DataFrame(data.copy())
    dfout = pd.DataFrame()
    if isinstance(window_size, int):
        dfout = pd.rolling_mean(data, window_size, min_periods=min_periods, center=center)
    elif isinstance(window_size, basestring):
        idx = pd.Series(data.index.to_pydatetime(), index=data.index)
        for colname, col in data.iterkv():
            result = idx.apply(f)
            result.name = colname
            dfout = dfout.join(result, how='outer')
    if dfout.columns.size == 1:
        dfout = dfout.ix[:,0]
    return dfout
    