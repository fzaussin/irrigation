from irrigation.inout import importdata
from irrigation.prep import interp, smooth

import matplotlib.pyplot as plt
from pytesmo import scaling

import pandas as pd


gpi = 695090
start_date = '2010-01-01'
end_date = '2010-12-31'

# read
data_object = importdata.QDEGdata()
ts = data_object.read_gpi(gpi, start_date, end_date, 'eraland', 'ascat', 'amsre')
# gapfill
ts_gapfill = interp.iter_fill(ts, 5)
ts_gapfill = ts_gapfill.dropna()
# scaling
ts_scaled = scaling.scale(ts_gapfill, 'mean_std', 0)

ts_smooth = smooth.iter_movav(ts_scaled, 35)


# increments
timedelta = pd.Timedelta('1 days')
ts_copy = ts_scaled.copy()

#print ts_copy

ts_copy_shift1 =  ts_copy.shift(1, timedelta)

# daily changes
deltas = ts_copy - ts_copy_shift1
#print deltas

# positive daily changes
pos_deltas = deltas[deltas > 0]
#print pos_deltas

# sum of pos increments
pos_deltas_sum = pos_deltas.sum()
print pos_deltas_sum

irrigation_ascat = pos_deltas_sum['ascat'] - pos_deltas_sum['eraland']
print "Estimated irrigation volume for ascat: {}".format(irrigation_ascat)
irrigation_amsre = pos_deltas_sum['amsre'] - pos_deltas_sum['eraland']
print "Estimated irrigation volume for amsre: {}".format(irrigation_amsre)

deltas.plot(kind='bar')
ts_scaled.plot()
ts_smooth.plot()
plt.show()