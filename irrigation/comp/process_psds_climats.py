import time
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from irrigation.prep import timeseries
from irrigation.comp import slopes


# define 1 model and multiple satellite datasets
models = ['merra']
satellites = ['ascat_reckless_rom']

# path to gpis
path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
gpis_lcmask = pd.DataFrame.from_csv(path)
gpis_lcmask = gpis_lcmask.sort_values('gpi_quarter')
gpis = gpis_lcmask['gpi_quarter']
total_gpis = len(gpis)

# init results container
results = []

tic = time.clock()
counter = 0
for gpi in gpis:
    counter += 1
    print "Processing gpi #{} of {}".format(counter, total_gpis)
    # exemplary slopes calc from climats for JJA
    # 721798 is mississippi example gpi
    try:
        df = timeseries.prepare(gpi=gpi,
                                start_date='2007-01-01',
                                end_date='2016-12-31',
                                models=models,
                                satellites=satellites,
                                kind='clim')
    except (IOError, ValueError):
        # skip gpi if no index for a location id can be found
        # problem with i=282 -> gpi #737696
        ascat = np.nan
        continue
    try:
        climat_slopes = slopes.slopes_climat(df)
        psdiffs = slopes.psd(climat_slopes)
        # slopes for JJA climat
        psdiffs_sum = psdiffs[151:243].sum()
        ascat = psdiffs_sum[0]
    except ValueError:
        # ValueError: if no data for gpi
        # IOError: if index for location id not found (gldas problem only?)
        ascat = np.nan

    results.append((gpi, ascat))
toc = time.clock()

df_results = pd.DataFrame(results, columns=('gpi', 'ascat'))
df_results.to_csv('/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/usa-jja-climats-merra-ascatreckrom-200701-201612.csv')

print "Elapsed time: ", str(datetime.timedelta(seconds=toc-tic))
