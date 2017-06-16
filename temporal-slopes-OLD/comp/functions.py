# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 11:32:47 2016

@author: fzaussin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 07 12:16:42 2016

@author: fzaussin

Slope Estimation 
ERA Land, ASCAT
"""

import os, sys
#sys.path.append('/home/fzaussin/shares/home/code')

import time

import numpy as np
import pandas as pd

from pytesmo import scaling
from pytesmo.time_series.anomaly import calc_climatology

# inout
from inout import import_data
from inout.import_data import QDEGdata
from inout import reader
# prep
from prep.preprocess import add_nan, fill_gaps
#trans
from trans.dates import date_range_mapper, check_years, date_range_string, current_time
# vis
from vis.info import temporal_slopes_info
from vis import spatialplot as mp

def apply_load_ts(x, start_date, end_date, product):
    """
    Load ts data of ASCAT/AMSRE/AMSR2 and ERA-LAND row-wise out of 
    lookup table, apply a gap-filling of 10 days and calculate the 
    climatologies. Then perform a scaling of the ERA-LAND ts to the 
    satellite data. 
    
    Parameters
    ----------
    x : arg to pass to pandas.apply func
        x[0] : Gpi in WARP Grid
        x[1] : Gpi in QDEG Grid
        x[2] : Gpi in ERA Grid
    start_date : string
        Start date of the analysis period
    end_date : string
        End date of the analysis period
    product : string
        'ascat', 'amsre' or 'amsr2'
        
    Returns
    -------
    data : pandas.DataFrame
        Dataframe containing the climatology or moving average of the product 
        and the scaled ERALAND ts
    """
    # TODO: allow multiple product inputs -> vectorize

    # read era-land ts
    ts_era = import_data.era_land_ts(x[2],
                                start_date,
                                end_date, 'daily_mean')['39'] * 100

    # TODO: create 1 reader that takes the product as an import argument and
    # outputs a series if only one is specified

    # read satellite data and gapfill
    if product == 'ascat':
        ts_sat = reader.ascat_ts(x[0], start_date, end_date)
        ts_sat = fill_gaps(add_nan(ts_sat))
    elif product == 'amsre':
        sat_data = QDEGdata().read_gpi(x[1], start_date, end_date, product)
        ts_sat = sat_data['amsre']
        ts_sat = fill_gaps(add_nan(ts_sat))
    elif product == 'amsr2':
        sat_data = QDEGdata().read_gpi(x[1], start_date, end_date, product)
        ts_sat = sat_data['amsr2']
        ts_sat = fill_gaps(add_nan(ts_sat), 20)

        # calc moving average (35 days) for 1 year and climatology for more years
    if check_years(start_date, end_date):
        climat_sat = calc_climatology(ts_sat, 1, 35)
        climat_era = calc_climatology(ts_era, 1, 35)
    else:
        climat_sat = calc_climatology(ts_sat, 5, 35)
        climat_era = calc_climatology(ts_era, 5, 35)

    # scale climats
    climat_era_scaled = scaling.mean_std(climat_era, climat_sat)

    data = pd.DataFrame()
    data['sat_clim'] = climat_sat
    data['era_clim'] = climat_era_scaled

    return data


# %%

def calc_slope_diff_sum(x, product, start_date, end_date, date_ranges):
    """
    Calculates the sum of the absolute differences between the slopes of
    the ASCAT and ERA-LAND climatologies during a specified timespan. Needs
    to be applied on a lookup-table which contains the corresponding
    grid points in both grids.
    
    Parameters
    ----------
    x : corresponding grid points in lookup table
        x[0] : Gpi in WARP Grid
        x[1] : Gpi in ERA Grid
    start_date : string
        Start date of the analysis period
    end_date : string
        End date of the analysis period
    date_ranges : list
        List containing months or seasons to analyze
    
    Returns
    -------
    Sum of slope differences : pd.Series
        Series of the structure: gpi_quarter, slope_diffs_sum 
        for every time_range
    """

    print 'Gpi: ', int(x[1])

    # initiate lists to store data and corresponding indexes
    s_data = [x[1]]
    s_index = ['gpi_quarter']

    # convert date ranges to days of year
    day_ranges = date_range_mapper(date_ranges)

    # calculate climatologies
    climats = apply_load_ts(x, start_date, end_date, product)

    # calc slopes using a convolution ("moving average slope")
    x_coords = np.arange(1, 367)
    window = [-1, 0, 1]

    climats['slopes_era'] = np.convolve(climats['era_clim'],
                                        window, mode='same') \
                            / np.convolve(x_coords, window, mode='same')
    climats['slopes_sat'] = np.convolve(climats['sat_clim'],
                                        window, mode='same') \
                            / np.convolve(x_coords, window, mode='same')

    # iterate through day_ranges list of tuples and calc slope_diff_sum
    for period in range(len(day_ranges)):
        date_range = date_range_mapper(day_ranges[period])
        start_day = day_ranges[period][0]
        end_day = day_ranges[period][1]

        slope_diffs = (climats['slopes_sat'][start_day:end_day]
                       - climats['slopes_era'][start_day:end_day])

        # calc sum of the positive slope differences
        pos_slope_diffs = slope_diffs[slope_diffs >= 0]
        slope_diff_sum = pos_slope_diffs.sum()

        # build series data and index
        s_data.append(slope_diff_sum)
        s_index.append(date_range)

    return pd.Series(s_data, index=s_index)


# %%

def process_slope_sums(product,
                       start_year=2010,
                       end_year=2010,
                       folder_name=''):
    """
    Calculate positive slope difference sum 
    """

    # import lookup table for warp or qdeg grid
    path_lkup = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/QDEG_WARP_ERA_Continental_USA.csv'
    lookup = pd.DataFrame.from_csv(path_lkup)

    # %%
    # TODO: rewrite path stuff to functions

    # year to date
    start_date = '{}-01-01'.format(start_year)
    end_date = '{}-12-31'.format(end_year)

    # define daterange string 
    years_info = date_range_string(start_date, end_date)
    sat_date_info = '{}_{}'.format(product, years_info)
    run_date_info = current_time()

    # output path definitions
    # TODO move path_base to slope_process
    path_base = '/home/fzaussin/shares/users/Irrigation/Data/output/test'
    folder_name = '{}_{}'.format(folder_name, run_date_info)
    path_results = os.path.join(path_base, folder_name, sat_date_info)
    # %%
    # define time ranges for analysis
    time_ranges = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                   'JJA', 'SON', 'AMJJASO']

    # calculate slope differences
    slope_diffs = lookup.apply(calc_slope_diff_sum,
                                      args=(product,
                                            start_date,
                                            end_date,
                                            time_ranges,),
                                      axis=1)

    # change dtype of gpi to int for map function
    slope_diffs['gpi_quarter'] = slope_diffs['gpi_quarter'].astype(int)

    map_title = '{} ({}, '.format(product.upper(), years_info)

    mp.spatial_plot_quarter_grid(slope_diffs,
                                 title=map_title,
                                 tag_title=True,
                                 tight=True,
                                 region='USA',
                                 cblabel="Positive Slope Difference Sum",
                                 cbrange=(0, 60),
                                 path=path_results)

    slope_diffs.to_csv('{}{}'.format(os.path.join(path_results,
                                                  sat_date_info),
                                     '.csv'))


# %%

def process_handler(start_year=2002,
                    end_year=2013,
                    version_name='v',
                    clims=False,
                    sensors=['ascat', 'amsre', 'amsr2']):
    """
    """
    # stop time
    start_time = time.clock()

    # maximal time ranges (ERALAND : 1979 - 2013 is the limiting factor)
    years_dict = {'ascat': (2007, 2013),
                  'amsre': (2002, 2011),
                  'amsr2': (2012, 2013)}

    # iterate trough sensor list and process
    for sensor in sensors:
        print sensor

        time_range_sensor = years_dict.get(sensor)
        min_year_sat = time_range_sensor[0]
        max_year_sat = time_range_sensor[1]

        # process single years between start_year and end_year (if data exists)
        if (start_year == 2002 and end_year == 2013 and not clims):
            # year range to array
            years = np.arange(time_range_sensor[0], time_range_sensor[1] + 1)
            print years

            for year in years:
                process_slope_sums(sensor, year, year, version_name)

                # print process infomation
                info_string = temporal_slopes_info(time.clock() - start_time,  # process time
                                                   sensors,
                                                   year,  # startyear
                                                   year)  # endyear
                print info_string

        # process climatologies for max_ranges
        elif (start_year == 2002 and end_year == 2013 and clims):
            process_slope_sums(sensor, min_year_sat, max_year_sat, version_name)

            # print process infomation
            info_string = temporal_slopes_info(time.clock() - start_time,  # process time
                                               sensors,
                                               min_year_sat,  # startyear
                                               max_year_sat)  # endyear
            print info_string

        else:
            error_message = 'Wrong input or not implemented yet.'
            return error_message
