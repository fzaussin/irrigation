from smap_io.reshuffle import reshuffle
from smap_io.interface import SMAPTs

from datetime import datetime

# data path definitions
in_path = '/home/fzaussin/shares/radar/Datapool_raw/SMAP/L3_P_v3'
out_path = '/home/fzaussin/smap-L3_P_v3'

# define date range as datetime (!) objects
start_date = datetime(2015,4,1)
end_date = datetime(2016,12,6)

# specific soil moisture params
param_list = ['soil_moisture', 'soil_moisture_error']

if __name__ == '__main__':
    import time, datetime

    tic = time.clock()
    # start process
    reshuffle(in_path,
              out_path,
              start_date,
              end_date,
              param_list,
              50)

    toc = time.clock()
    print "Elapsed time: ", str(datetime.timedelta(seconds=toc - tic))