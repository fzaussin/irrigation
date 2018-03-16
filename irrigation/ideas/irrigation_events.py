"""
test summer job method again for different sat datasets
"""

import pandas as pd
from irrigation.inout import importdata
from trans.transform import qdeg2lonlat
from prep import interp
from ideas import precipitation
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

def read_sm(gpi, start_date, end_date):
    """"""


    # read sm data
    smdata = importdata.QDEGdata()
    sm = smdata.read_gpi(gpi, start, end,
                         models='merra',
                         satellites=['ascat',
                                     'ascatrecklessrom',
                                     'amsr2'])
    # fill small gaps
    sm = sm[start_date:end_date]
    sm = interp.iter_fill(sm, 3)
    return sm

def read_prec(gpi, start_date, end_date):
    """"""
    #lon, lat = qdeg2lonlat(gpi)
    # read trmm data
    prec = precipitation.trmm_reader(gpi)
    prec = prec[start_date:end_date]
    return prec.resample('D').sum()



if __name__=='__main__':

    # info
    gpi = 726000
    start = '2013-01-01'
    end = '2016-12-31'

    sm = read_sm(gpi, start, end)
    sm.plot(title="Gpi = {}".format(gpi))

    prec = read_prec(gpi, start, end)
    prec.plot()

    # IRRIGATION EVENTS
    # calc daily change in sm
    sm_changes = sm - sm.shift(1)
    # changes bigger than x percent
    thresh = 5

    irrig_events = pd.DataFrame(index=sm_changes.index)
    for series in sm_changes:
        cond1 = (sm_changes[series] > thresh)
        cond2 = (prec == 0)
        irrig_events[series] = sm_changes[series][cond1 & cond2]
    print irrig_events

    irrig_events['ascat'].plot(x='x', y='y', style='.', color='blue')
    irrig_events['ascatrecklessrom'].plot(x='x', y='y', style='.', color='purple')
    irrig_events['amsr2'].plot(x='x', y='y', style='.', color='grey')
    irrig_events['merra'].plot(x='x', y='y', style='.', color='red')

    agg = irrig_events.resample('Q-NOV').sum()
    agg.plot(kind='bar', title='Seasonal sum of SSM increases through irrigation')
    plt.show()

