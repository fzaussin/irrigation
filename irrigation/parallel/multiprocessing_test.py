import multiprocessing as mp
import time, datetime
import pandas as pd

# using the Pool class
def cube(x):
    return x**3


# test on gpi list
gpis_path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed+irrigated_thresh5_global.csv'
gpis_lcmask = pd.DataFrame.from_csv(gpis_path)
gpis = gpis_lcmask.index.values

if __name__=='__main__':
    tic = time.clock()
    pool = mp.Pool(processes=8)
    results = pool.map(cube, gpis)
    toc = time.clock()
    print results
    print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))
