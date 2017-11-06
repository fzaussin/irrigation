# -*- coding: utf-8 -*-

"""
Idea: irrigated areas show lower difference between min and max sm value than
non irrigated areas

"""
import pandas as pd
from inout.importdata import QDEGdata
from irrigation.prep import interp, smooth


def yearly_range(ts):
    """Calculates range of SM values of seasonal ts pattern."""
    yearly_min = ts.resample('A').min()
    yearly_max = ts.resample('A').max()

    return yearly_max - yearly_min

if __name__ == "__main__":

    import os
    import time
    import datetime
    import logging

    import matplotlib.pyplot as plt
    from irrigation.prep import timeseries
    from irrigation.comp import slopes

    import numpy as np
    import pandas as pd

    data = QDEGdata()

    ################################################################################
    # DEFINE PROCESS
    # output folder
    out_root = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/yearly-range'

    # information on processing run and location info
    info = 'Yearly min-max range'
    region = 'usa'

    # define 1 (!) model and multiple satellite datasets
    satellites = ['ascatrecklessrom']

    ################################################################################
    # set path to gpis
    gpis_path_usa = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'

    # create gpi list
    gpis_lcmask = pd.DataFrame.from_csv(gpis_path_usa)
    total_gpis = len(gpis_lcmask)

    # init dfs as containers
    dict_of_dfs = {}
    for sat in satellites:
        dict_of_dfs[str(sat)] = pd.DataFrame()

    # iterate over gpis and process at each pixel
    tic = time.clock()
    counter = 0
    for row in gpis_lcmask.itertuples():
        counter = counter + 1
        gpi = row[1]
        crop_fraction = row[2]

        print "Processing at gpi #{counter} of {total}".format(counter=counter, total=total_gpis)
        # read smoothed ts
        try:
            df = data.read_gpi(gpi, '2007-01-01', '2016-12-31',
                               models=[],
                               satellites=['ascatrecklessrom'])
            if df.empty:
                raise IOError
        except (IOError, RuntimeError, ValueError):
            print "No data for gpi #{gpi}".format(gpi=gpi)
            for key, value in dict_of_dfs.iteritems():
                value[str(gpi)] = np.nan
            continue
        try:
            # calculate yearly min-max range
            ts_smoothed = smooth.iter_movav(df, 35)
            y_range = yearly_range(ts_smoothed)

            for key, value in dict_of_dfs.iteritems():
                value[str(gpi)] = y_range[key]
        except ValueError:
            for key, value in dict_of_dfs.iteritems():
                value[str(gpi)] = np.nan

    # transpose and save to .csv
    for key, value in dict_of_dfs.iteritems():
        df_out = value.transpose()
        # generate fname
        fname = "{region}_{satellite}.csv".format(
            region=region,
            satellite=key)
        df_out.to_csv(os.path.join(out_root, fname))

    toc = time.clock()
    print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))
    print "Results saved to: {}".format(out_root)
