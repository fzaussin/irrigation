import os
import time
import datetime
import logging

import matplotlib.pyplot as plt
from irrigation.prep import timeseries
from irrigation.comp import slopes

import numpy as np
import pandas as pd

################################################################################
# DEFINE PROCESS
# output folder
out_root = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/italians-metric-test-usa'

# information on processing run and location info
info = 'Test of the metric the italians used. The considered only slopes where dsm_sat > 0 & dsm_mod <= 0 and counted the ocurrences during the irrigation season' \
       'these results represent seasonal counts'
region = 'usa'

# define 1 (!) model and multiple satellite datasets
models = ['merra']
satellites = ['ascat_reckless_rom', 'amsr2']

# 'Q-NOV' for seasonal, 'M' for monthly results
resampling = 'Q-NOV'

# start- and end-dates of analysis period
start = '2013-01-01'
end = '2016-12-31'

# path to gpis
# usa: '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
# global: '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed+irrigated_thresh5_global.csv'
################################################################################
# set path
gpis_path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
gpis_lcmask = pd.DataFrame.from_csv(gpis_path)
total_gpis = len(gpis_lcmask)
# init dfs as containers
dict_of_dfs = {}
for sat in satellites:
    dict_of_dfs[str(sat)] = pd.DataFrame()

tic = time.clock()
counter = 0
for row in gpis_lcmask.itertuples():
    # error sigsegv for gpi 266372
    counter = counter + 1
    gpi = row[1]
    print "Processing {model} with {satellites} at gpi #{counter} of {total}".format(model=model,
                                                                                     satellites=satellites,
                                                                                     counter=counter,
                                                                                     total=total_gpis)
    # read smoothed ts
    try:
        df = timeseries.prepare(gpi=gpi,
                           start_date=start,
                           end_date=end,
                           models=models,
                           satellites=satellites,
                           kind=None)


        if df.empty:
            raise IOError
    except (IOError, RuntimeError, ValueError):
        # ValueError: Index of time series for location id #1482116 not found
        # skip gpi if no index for a location id can be found
        # problem with i=282 -> gpi #737696
        print "No data for gpi #{gpi}".format(gpi=gpi)
        for key, value in dict_of_dfs.iteritems():
            value[str(gpi)] = np.nan
        continue
    try:
        # calculate slopes:
        # slopes_movav is with convolution
        #df_slopes = slopes.slopes_movav(df)
        # local_slopes is differential quotient
        df_slopes = slopes.diffquot_slope(df)

        #TODO: testing the metric of the italians
        psd_sum = slopes.slope_metric_italians(df_slopes)
        for key, value in dict_of_dfs.iteritems():

            value[str(gpi)] = psd_sum[key]

    except ValueError:
        # ValueError: if no data for gpi
        # IOError: if index for location id not found (gldas problem only?)
        for key, value in dict_of_dfs.iteritems():
            value[str(gpi)] = np.nan

# transpose and save to .csv
for key, value in dict_of_dfs.iteritems():
    df_out = value.transpose()
    # generate fname
    fname = "{region}_{model}_{satellite}_{start}_{end}.csv".format(
        region=region,
        model=models,
        satellite=key,
        start=start,
        end=end)
    df_out.to_csv(os.path.join(out_root, fname))

toc = time.clock()
print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))
print "Results saved to: {}".format(out_root)


# create basic log file with process information
logging.basicConfig(filename=os.path.join(out_root,'info.log'), level=logging.DEBUG)
logging.info('INFORMATION: {}'.format(info))
logging.info('Model data: {}'.format(models))
logging.info('Satellite data: {}'.format(satellites))
logging.info('Date range: {} to {}'.format(start, end))
logging.info("Elapsed time: {}".format(str(datetime.timedelta(seconds=toc - tic))))
logging.info("Finished processing at {}".format(str(datetime.datetime.now())))
