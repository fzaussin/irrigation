import time
import datetime
import matplotlib.pyplot as plt
from irrigation.prep import timeseries
from irrigation.comp import slopes

import numpy as np
import pandas as pd

# init output containers
df_ascat = pd.DataFrame()
df_amsre = pd.DataFrame()

# path to gpis
path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
gpis_lcmask = pd.DataFrame.from_csv(path)
gpis = gpis_lcmask['gpi_quarter']

tic = time.clock()
for gpi in gpis:
    print gpi
    # read smoothed ts
    try:
        df = timeseries.prepare(gpi=gpi,
                                start_date='2007-01-01',
                                end_date='2011-12-31',
                                kind='movav')
    except (IOError, RuntimeError):
        # skip gpi if no index for a location id can be found
        # problem with i=282 -> gpi #737696
        df_ascat[str(gpi)] = np.nan
        df_amsre[str(gpi)] = np.nan
        continue
    try:
        # aggregate psds
        df_slopes = slopes.slopes_movav(df)
        df_psd = slopes.psd(df_slopes)
        agg = slopes.aggregate_psds(df_psd, 'Q-NOV')
        # append to sat df
        df_ascat[str(gpi)] = agg['ascat']
        df_amsre[str(gpi)] = agg['amsre']
    except ValueError:
        # ValueError: if no data for gpi
        # IOError: if index for location id not found (gldas problem only?)
        df_ascat[str(gpi)] = np.nan
        df_amsre[str(gpi)] = np.nan

# transpose
df_ascat_out = df_ascat.transpose()
df_amsre_out = df_amsre.transpose()
# save to csv
df_ascat_out.to_csv('/home/fzaussin/Desktop/TEST_USA_gldas_ascat_seasonal.csv')
df_amsre_out.to_csv('/home/fzaussin/Desktop/TEST_USA_gldas_amsre_seasonal.csv')

toc = time.clock()
print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))
