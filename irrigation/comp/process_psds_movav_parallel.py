import os
import time
import datetime
import logging

import matplotlib.pyplot as plt
from irrigation.prep import timeseries
from irrigation.comp import slopes

import numpy as np
import pandas as pd

import multiprocessing as mp
# KILL: kill -9 `ps -ef | grep process_psds_movav_parallel.py | grep -v grep | awk '{print $2}'` -> in terminal

################################################################################
# GLOBAL INFO
################################################################################
out_root = '/home/fzaussin/Desktop/parallel-test'

# information on processing run and location info
info = 'parallel test'
region = 'usa'

# define 1 (!) model and multiple satellite datasets
models = ['merra']
satellites = ['ascat_reckless_rom', 'amsr2', 'smap']

# 'Q-NOV' for seasonal, 'M' for monthly results
resampling = 'Q-NOV'

# start- and end-dates of analysis period
start = '2015-04-01'
end = '2016-12-31'

################################################################################

def process_in_parallel(gpi):
    """"""
    print gpi

    # read smoothed ts
    try:
        df = timeseries.prepare(gpi=gpi,
                                start_date=start,
                                end_date=end,
                                models=models,
                                satellites=satellites,
                                kind='movav')
        if df.empty:
            raise IOError
    except (IOError, RuntimeError, ValueError, RuntimeWarning):
        print "No data for gpi #{gpi}".format(gpi=gpi)
        return pd.DataFrame()
    try:
        df_slopes = slopes.diffquot_slope(df)
        df_psd = slopes.psd(df_slopes)
        psd_sum = slopes.aggregate_psds(df_psd, resampling)
        # associate with corresponding gpi
        psd_sum['gpi'] = gpi
    except ValueError:
        return pd.DataFrame()
    return psd_sum


if __name__=='__main__':
    import multiprocessing

    tic = time.time()
    # create gpi list to process
    gpis_path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
    gpis_lcmask = pd.DataFrame.from_csv(gpis_path)
    gpis = gpis_lcmask['gpi_quarter'].values
    print gpis

    # parallel processing
    pool = mp.Pool(processes=8)
    try:
        # results is list of tuples where [0]=gpi, [1]=dict of data frames
        results = pool.map(process_in_parallel, gpis)
        print results
    except KeyboardInterrupt:
        print("Caught it")
        pool.close()
    except TypeError:
        print 'here it is'
        pass
    # drop gpis where we have no data
    cleaned_results = [x for x in results if not x.empty]
    dfs_out = pd.concat(cleaned_results)
    # TODO: MUCH TO DO...

    # write temporary results
    print "Writing results..."
    fname = "{region}_{model}_{satellite}_{start}_{end}.csv".format(
        region=region,
        model=models,
        satellite='-'.join(satellites),
        start=start,
        end=end)

    dfs_out.to_csv(os.path.join(out_root, fname))

    toc = time.time()
    print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))