# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 11:30:05 2016

@author: fzaussin

Positive slope differences - Process

current path_base = r"D:\_data\_Results\Slope_Analysis"
"""
from comp.functions import process_handler

# Choose version-name
version_name = 'test-13072017'

# Choose time range
# TODO: allow other input as 2002-2013, write description
# error handling
# 2002-2013 -> means process all existing data in that range

start_year = 2002
end_year = 2013

# Calculate climatologies (optional, defaults to False)
clims = True

# Define sensors to process (optional, defaults to all)
sensors = ['ascat', 'amsre', 'amsr2']

# Start process
process_handler(start_year, end_year, version_name, clims, sensors)