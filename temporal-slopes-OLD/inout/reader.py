# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 16:53:25 2016

@author: fzaussin

Read routines
"""

import pandas as pd
import numpy as np

from warp_data.interface import WARP
from rsdata.ECMWF.interface import ERALAND_g2ze
from rsdata.AMSRE.interface import LPRMv5

from datetime import timedelta
import pytesmo.timedate.julian as julian
from pygeogrids.grids import BasicGrid, genreg_grid


###############################################################################
# ASCAT 
###############################################################################

# Configuration file
#cfg = '/home/fzaussin/shares/users/Irrigation/Data/input/WARP/datasets/foxy_finn/foxy_finn.cfg'
"""
cfg = '/home/fzaussin/shares/radar/Datapool_processed/WARP/datasets/foxy_finn/R1A/IRMA1_WARP56_P1R1.cfg'
ssm = WARP(cfg,'ssm')
ssf = WARP(cfg,'ssf')


def read_warp_ssm(ssm,ssf,gpi):
    ssm_ts = ssm.read_ts(gpi)
    ssf_ts = ssf.read_ts(gpi)
    
    # ceil or round?
    jd = np.ceil(ssm_ts['jd']-0.5)+0.5
    ts = pd.DataFrame(ssm_ts, index=julian.julian2datetimeindex(jd))
    ts['ssf'] = ssf_ts['ssf']
    
    ts = ts[(ts['proc_flag']<=2)&(ts['ssf']==1)]['sm']
    ts.index.tz = None
    
    return ts.groupby(level=0).last()
    
def ascat_ts(gpi, start_date, end_date):
    ts = read_warp_ssm(ssm,ssf,gpi)
    return ts[start_date:end_date]
    
"""

def era_land_ts(gpi_era, start_date, end_date, temp_res='daily_mean'):
    """
    Read ERA-LAND Soil Moisture Timeseries (Parameter=39) at ERA Gpi
    """
    
    ts = ERALAND_g2ze().read_ts(gpi_era)[start_date:end_date]
    
    if ts.empty:
        error_message = 'No data available at this date.'
        return error_message
    
    if temp_res == 'daily_mean':
        ts = ts.resample('D').mean()
        return ts
    else:
        return ts

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    ts = era_land_ts(21221, '2007-01-01', '2013-12-31')
    print ts
    ts.plot()
    plt.show()
