# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 12:33:17 2016

@author: fzaussin

Functions for ts date operations
"""

import numpy as np
import pandas as pd

import datetime
from time import gmtime, strftime


def date_range_mapper(date_ranges):
        
    date_dict = {'Jan' : (0,31), 
                 'Feb' : (31,59),
                 'Mar' : (59,90),
                 'Apr' : (90,120),
                 'May' : (120,151),
                 'Jun' : (151,181),
                 'Jul' : (181,212),
                 'Aug' : (212,243),
                 'Sep' : (243,273),
                 'Oct' : (273,304),
                 'Nov' : (304,334),
                 'Dec' : (334,365),
                 'MAM' : (59,151),
                 'JJA' : (151,243),
                 'SON' : (243,334),
                 'AMJJASO' : (90,304)}
    
        # input = 1 value
    if type(date_ranges) is not list and date_ranges in date_dict.values():
        for key, val in date_dict.iteritems():
            if date_ranges == val:
                return key
    # input = keys
    elif all(date in date_dict.keys() for date in date_ranges):
        values = [date_dict[x] for x in date_ranges]
        return values
        
    # input = values
    elif all(vals in date_dict.values() for vals in date_ranges):
        keys = []
        for key, val in date_dict.iteritems():
            if val in date_ranges:
                keys.append(key)
        return keys
        
    else: 
        error_message = 'You entered an unknown date range.'
        return error_message

def check_years(start_date, end_date):
    """
    """ 
    start_year = start_date[0:4]
    end_year = end_date[0:4]
    
    if start_year == end_year:
        return True
    else:
        return False
        
def date_range_string(start_date, end_date):
    """
    """
    start_year = start_date[0:4]
    end_year = end_date[0:4]
    
    if start_year == end_year:
        years = '{}'.format(start_year)
    else:
        years = '{}-{}'.format(start_year, end_year)
        
    return years
    
    
def process_info(process_seconds, sensors, start_year, end_year):
    """
    Print process information
    """
    process_time = str(datetime.timedelta(seconds=process_seconds))
        
    info_string = ('\nPROCESS_INFO:'
                    '\nProcess-Time : {}'
                    '\nDate-Range : {}-{}'
                    '\nSensors : {}\n'.format(process_time,
                                              start_year,
                                              end_year,
                                              sensors))                                                                      
    return info_string
    
    
def time_ranges_dict(start_year, 
                     end_year, 
                     clims=False,
                     sensors = ['ascat', 'amsre', 'amsr2']):
    """
    """      

    if clims:
        time_ranges = [(start_year, end_year)] * len(sensors)
    else:
        # single years
        time_ranges = np.arange(start_year, end_year + 1) 
    
    return time_ranges
 
def datenum2date(x):
    """
    Converts Matlabs datenum format to a pandas timestamp
    """
    python_datetime = pd.datetime.fromordinal(int(x[0])) + pd.Timedelta(days=x[0]%1) - pd.Timedelta(days = 366)
    timestamp = pd.to_datetime(python_datetime)    
    return timestamp
    
def current_time(date_only=True):
    """
    """
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if date_only:
        return time[:10]
    else:
        return time