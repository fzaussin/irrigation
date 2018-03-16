import time
import datetime

import numpy as np
import pandas as pd

from irrigation.prep import timeseries
from irrigation.comp import slopes


date_dict = {'Jan' : (0,31),
             'Feb' : (31,60),
             'Mar' : (60,91),
             'Apr' : (91,121),
             'May' : (121,152),
             'Jun' : (152,182),
             'Jul' : (182,213),
             'Aug' : (213,244),
             'Sep' : (244,274),
             'Oct' : (274,305),
             'Nov' : (305,335),
             'Dec' : (335,366),
             'MAM' : (60,152),
             'JJA' : (152,244),
             'SON' : (244,335),
             'AMJJA': (91,244),
             'JJAS': (152,274)}


if __name__=='__main__':
    # define 1 model and multiple satellite data sets
    models = ['merra']
    satellites = ['smapv4']
    
    # path to gpis
    path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv'
    gpis_lcmask = pd.DataFrame.from_csv(path)
    gpis_lcmask = gpis_lcmask.sort_values('gpi_quarter')
    gpis = gpis_lcmask['gpi_quarter']
    total_gpis = len(gpis)

    # init results container
    results = {}

    tic = time.clock()
    counter = 0
    for row in gpis_lcmask.itertuples():
        counter += 1

        gpi = row[1]
        crop_fraction = row[2]
        print "Processing gpi #{} of {}".format(counter, total_gpis)
        # exemplary slopes calc from climats for JJA
        # 721798 is mississippi example gpi
        try:
            df = timeseries.prepare(gpi=gpi,
                                            start_date='2012-01-01',
                                            end_date='2016-12-31',
                                            models=models,
                                            satellites=satellites,
                                            kind='clim')
            if df.empty:
                sat = np.nan
        except (IOError, ValueError):
            # skip gpi if no index for a location id can be found
            # problem with i=282 -> gpi #737696
            sat = np.nan
        try:
            climat_slopes = slopes.diffquot_slope_climat(df)
            psdiffs = slopes.psd(climat_slopes)
            psds4dates = pd.Series(index=date_dict.keys())
            # iterate over date ranges
            for id, date_range in date_dict.iteritems():
                psds4dates[id] = psdiffs[date_range[0]:date_range[1]].sum()
            
            # slopes for JJA climat
            # divide by fractional crop AREA (!)
            sat = psds4dates
        except ValueError:
            # ValueError: if no data for gpi
            # IOError: if index for location id not found (gldas problem only?)
            sat = np.nan

        results.update({str(gpi): sat})
    toc = time.clock()

    #print pd.concat(results.values(), axis=1)
    resultsT = pd.concat(results, axis=1)
    # transpose and correctly set zeros to nan
    df_results = resultsT.transpose() #.replace(0, np.nan)
    df_results.to_csv('/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/FIXED/NEW-METRIC/USA/climats/smapv4-merra-climat-based.csv')

    print "Elapsed time: ", str(datetime.timedelta(seconds=toc-tic))

