import os
import time
import datetime
import logging

from irrigation.inout import importdata
from irrigation.prep import interp

from pytesmo import scaling

import numpy as np
import pandas as pd


def prepare_ts(gpi, start_date, end_date, models, satellites):
    """"""
    # read ts
    data_object = importdata.QDEGdata()
    ts = data_object.read_gpi(gpi, start_date, end_date, models, satellites)
    # gapfill
    ts_gapfill = interp.iter_fill(ts, 5)
    ts_gapfill = ts_gapfill.dropna()
    # scaling
    ts_scaled = scaling.scale(ts_gapfill, 'mean_std', 0)
    return ts_scaled

def calc_deltas(ts_scaled):
    ts_copy = ts_scaled.copy()
    # daily changes
    deltas = ts_copy - ts_copy.shift(1)
    # positive daily changes
    return deltas

def calc_irrig(deltas, resampling='Q-NOV'):
    """
    Sum of positive sm increments in satellite soil moisture where model sm slopes
    are zero or negative over the period specified by resampling.
    :param deltas:
    :param resampling:
    :return:
    """
    reference_index = 0
    model_slopes = deltas[deltas.columns.values[reference_index]]
    satellite_slopes = deltas.drop([deltas.columns.values[reference_index]], axis=1)

    # apply conditions for irrigation event
    model_slopes[model_slopes > 0] = np.nan
    satellite_slopes[satellite_slopes <= 0] = np.nan
    model_cond_bool = pd.isnull(model_slopes)

    satellite_slopes[model_cond_bool] = np.nan
    return satellite_slopes.resample(resampling).sum()


def irrig_increments(gpi, start_date, end_date, resampling='Q-NOV'):
    """"""
    ts_scaled = prepare_ts(gpi, start_date, end_date, models=['merra'], satellites=['ascat_reckless_rom'])
    deltas = calc_deltas(ts_scaled)
    irrig = calc_irrig(deltas, resampling)
    return irrig


if __name__=='__main__':
    # process for us
    import matplotlib
    matplotlib.style.use('ggplot')
    """
    #SIMPLE PLOT
    gpi = 758408

    start_date = '2007-01-01'
    end_date = '2016-12-31'

    df = prepare_ts(gpi, start_date, end_date)
    df.plot(title='input ts')

    df_irrig = irrig_increments(gpi, start_date, end_date, resampling='Q-NOV')
    ax = df_irrig.plot(title='Sum of positive satellite soil moisture increments')
    ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax.set_xlabel('Datetime')
    plt.show()
    """
    ################################################################################
    # DEFINE PROCESS
    # output folder
    out_root = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/sat-soilmoisture-increments-sum'

    # information on processing run and location info
    info = 'sum of positive satellite soil moisture increments where the model sm slope is zero or negative'
    region = 'usa'

    # define 1 (!) model and multiple satellite datasets
    models = ['merra']
    satellites = ['ascat_reckless_rom', 'amsr2', 'smap']

    # 'Q-NOV' for seasonal, 'M' for monthly results
    resampling = 'Q-NOV'

    # start- and end-dates of analysis period
    start = '2016-01-01'
    end = '2016-12-31'

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
        crop_fraction = row[2]  # + row[3]
        print "Processing {model} with {satellites}"" \
        ""at gpi #{counter} of {total}".format(model=models,
                                               satellites=satellites,
                                               counter=counter,
                                               total=total_gpis)
        # read smoothed ts
        try:
            ts = prepare_ts(gpi=gpi,
                            start_date=start,
                            end_date=end,
                            models=models,
                            satellites=satellites)
            if ts.empty:
                raise IOError
        except (IOError, RuntimeError, ValueError):
            print "No data for gpi #{gpi}".format(gpi=gpi)
            for key, value in dict_of_dfs.iteritems():
                value[str(gpi)] = np.nan
            continue
        try:
            # calculate slopes
            deltas = calc_deltas(ts)
            irrig_sum = calc_irrig(deltas, resampling=resampling)

            # append to sat df
            for key, value in dict_of_dfs.iteritems():
                value[str(gpi)] = irrig_sum[key]
        except ValueError:
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
    logging.basicConfig(filename=os.path.join(out_root, 'info.log'),
                        level=logging.DEBUG)
    logging.info('INFORMATION: {}'.format(info))
    logging.info('Model data: {}'.format(models))
    logging.info('Satellite data: {}'.format(satellites))
    logging.info('Date range: {} to {}'.format(start, end))
    logging.info(
        "Elapsed time: {}".format(str(datetime.timedelta(seconds=toc - tic))))
    logging.info(
        "Finished processing at {}".format(str(datetime.datetime.now())))
