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
out_root = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/FIXED/NEW-METRIC/USA/35-day-movav/monthly'

# information on processing run and location info
info = 'Fixed data gaps for every sat single processing' \
       '5-day gapfilling, nan-sensitive scaling'
region = 'usa'

# define 1 (!) model and multiple satellite datasets
models = ['merra']
satellites = ['ascatrecklessrom', 'amsr2', 'smapv4'] #, 'amsr2', 'smap', 'smapv4', 'ascatrecklessrom']

# 'Q-NOV' for seasonal, 'M' for monthly results
resampling = 'M'
window = 35

# start- and end-dates of analysis period
start = '2015-01-01'
end = '2016-12-31'

################################################################################
# set path to gpis
gpis_path_usa = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
gpis_path_global = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed+irrigated_thresh5_global.csv'
gpis_usa = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/QDEG_pointlist_USA_cut.csv'
# temp
gpis_cali = '/home/fzaussin/data/california_gpis.csv'
gpis_idaho = '/home/fzaussin/data/gpis_idaho.csv'
gpis_mississ = '/home/fzaussin/data/gpis_mississ.csv'


# create gpi list
gpis = pd.DataFrame.from_csv(gpis_path_usa) #.index
total_gpis = len(gpis)

# init dfs as containers
dict_of_dfs = {}
for sat in satellites:
    dict_of_dfs[str(sat)] = pd.DataFrame()

# iterate over gpis and process at each pixel
tic = time.clock()
counter = 0
for row in gpis.itertuples():
    counter = counter + 1
    gpi = row[1]
    #crop_fraction = row[2]

    print "Processing {model} with {satellites}"" \
    ""at gpi #{counter} of {total}".format(model=models,
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
                                kind='movav',
                                window=window)
        if df.empty:
            raise IOError
    except (IOError, RuntimeError, ValueError):
        print "No data for gpi #{gpi}".format(gpi=gpi)
        for key, value in dict_of_dfs.iteritems():
            value[str(gpi)] = np.nan
        continue
    try:
        # calculate slopes
        df_slopes = slopes.diffquot_slope(df)
        df_psd = slopes.new_slope_metric(df_slopes)
        psd_sum = slopes.aggregate_psds(df_psd, resampling)
        # divide by fractional crop AREA (!)
        #psd_sum = np.divide(psd_sum, (crop_fraction*25*25))

        # append to sat df
        for key, value in dict_of_dfs.iteritems():
            value[str(gpi)] = psd_sum[key]
    except ValueError:
        for key, value in dict_of_dfs.iteritems():
            value[str(gpi)] = np.nan

# transpose and save to .csv
for key, value in dict_of_dfs.iteritems():
    df_out = value.transpose()
    # generate fname
    fname = "{region}_{model}_{satellite}_{start}_{end}.csv".format(
        region=region,
        model=''.join(models),
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
logging.info('Model data: {}'.format(''.join(models)))
logging.info('Satellite data: {}'.format(satellites))
logging.info('Date range: {} to {}'.format(start, end))
logging.info("Elapsed time: {}".format(str(datetime.timedelta(seconds=toc - tic))))
logging.info("Finished processing at {}".format(str(datetime.datetime.now())))
