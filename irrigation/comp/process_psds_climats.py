import time
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from irrigation.prep import timeseries
from irrigation.comp import slopes


# define 1 model and multiple satellite datasets
model = 'eraland'
satellites = ['ascat', 'amsre']

# path to gpis
path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
gpis_lcmask = pd.DataFrame.from_csv(path)
gpis = gpis_lcmask['gpi_quarter']


tic = time.clock()
results = []
for gpi in gpis:
    print gpi
    # exemplary slopes calc from climats for JJA
    # 721798 is mississippi example gpi
    try:
        df = timeseries.prepare(gpi=gpi,
                                start_date='2007-01-01',
                                end_date='2011-12-31',
                                model=model,
                                satellites=satellites,
                                kind='movav')
    except IOError:
        # skip gpi if no index for a location id can be found
        # problem with i=282 -> gpi #737696
        ascat = np.nan
        amsre = np.nan
        continue
    try:
        climat_slopes = slopes.slopes_climat(df)
        psdiffs = slopes.psd(climat_slopes)
        # slopes for JJA climat
        psdiffs_sum = slopes.psds(psdiffs, 151, 243)
        # for each sat
        amsre = psdiffs_sum[0]
        ascat = psdiffs_sum[1]
    except ValueError:
        # ValueError: if no data for gpi
        # IOError: if index for location id not found (gldas problem only?)
        ascat = np.nan
        amsre = np.nan

    results.append((gpi, ascat, amsre))
toc = time.clock()

df_results = pd.DataFrame(results, columns=('gpi', 'ascat', 'amsre'))
df_results.to_csv('/home/fzaussin/Desktop/TEST_USA_ascat_gldas_climat_psds_JJA.csv')

print "Elapsed time: ", str(datetime.timedelta(seconds=toc-tic))
