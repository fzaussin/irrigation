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
out_root = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/merra-smap-egypt-test'

# information on processing run and location info
info = 'test for smap and merra over egypt - large irrigation district'
region = 'egypt'

# define 1 (!) model and multiple satellite datasets
model = 'merra'
satellites = ['smap']

# 'Q-NOV' for seasonal, 'M' for monthly results
resampling = 'M'

# start- and end-dates of analysis period
start = '2015-01-01'
end = '2016-12-31'

# set path
gpis_path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/merra-smap-egypt-test/ptlist_irrigation_district_egypt.csv'
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
    crop_fraction = row[2] + row[3]
    print "Processing {model} with {satellites} at gpi #{counter} of {total}".format(model=model,
                                                                                     satellites=satellites,
                                                                                     counter=counter,
                                                                                     total=total_gpis)
    # read smoothed ts
    try:
        df = timeseries.prepare(gpi=gpi,
                                start_date=start,
                                end_date=end,
                                model=model,
                                satellites=satellites,
                                kind='movav')
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
        df_psd = slopes.psd(df_slopes)
        # aggregate psd for seasons
        psd_sum = slopes.aggregate_psds(df_psd, resampling)
        # append to sat df
        # normalize to area fraction # psds[m^3/m^3] / crop_fraction [%] * pixel_area [km^2]
        for key, value in dict_of_dfs.iteritems():
            #value[str(gpi)] = np.divide((psd_sum[key] * crop_fraction),
            #                            (12.5 * 12.5))
            value[str(gpi)] = np.multiply(psd_sum[key], crop_fraction)

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
        model=model,
        satellite=key,
        start=start,
        end=end)
    df_out.to_csv(os.path.join(out_root, fname))

toc = time.clock()
print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))


# create basic log file with process information
logging.basicConfig(filename=os.path.join(out_root,'info.log'), level=logging.DEBUG)
logging.info('INFORMATION: {}'.format(info))
logging.info('Model data: {}'.format(model))
logging.info('Satellite data: {}'.format(satellites))
logging.info('Date range: {} to {}'.format(start, end))
logging.info("Elapsed time: {}".format(str(datetime.timedelta(seconds=toc - tic))))
logging.info("Finished processing at {}".format(str(datetime.datetime.now())))
