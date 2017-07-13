import pytesmo.io.ismn.interface as ismn
from irrigation.ideas.precipitation import trmm_reader
from pytesmo.validation_framework import temporal_matchers
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks", context='poster')

path_to_ismn_data = '/home/fzaussin/shares/users/Irrigation/Data/input/ismn/spain'
ISMN_reader = ismn.ISMN_Interface(path_to_ismn_data)

networks = ISMN_reader.list_networks()
print "Available Networks:"
print networks

network = networks[0]
stations = ISMN_reader.list_stations(network = network)
print "Available Stations in Network %s"%network
print stations

# select the irrigated station
station = 'Canizal'
station_obj = ISMN_reader.get_station(station)
print "Available Variables at Station %s"%station
#get the variables that this station measures
variables = station_obj.get_variables()
print 'variables: ', variables

depths_from, depths_to = station_obj.get_depths(variables[0])
sensors = station_obj.get_sensors(variables[0],depths_from[0],depths_to[0])
print 'sensors: ', sensors


# SOIL MOISTURE
sm_depht_from,sm_depht_to = station_obj.get_depths('soil moisture')
print sm_depht_from,sm_depht_to
sensors = station_obj.get_sensors('soil moisture', sm_depht_from[0],
                                  sm_depht_to[0])
#read sm data measured in first layer 0-0.05m
sm = station_obj.read_variable('soil moisture',depth_from=sm_depht_from[0],depth_to=sm_depht_to[0], sensor=sensors[0])
sm_ts_natres = sm.data['soil moisture']

# TRMM PRECIPITATION
lon_station, lat_station = (-5.35883903503418, 41.195999523)
prec_ts_natres = trmm_reader(lon_station, lat_station)


# resample to daily res
resampling = 'D'
sm_ts = sm_ts_natres.resample(resampling).mean()
prec_ts = prec_ts_natres.resample(resampling).sum()

# combine to df
df_sm_prec = pd.DataFrame(index=sm_ts.index)
df_sm_prec['sm'] = sm_ts
df_sm_prec['prec'] = prec_ts
# end date of trmm data
df_sm_prec = df_sm_prec[:'2015-08-31']

ax = df_sm_prec['sm'].plot(ylim=(0,1))
ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

ax = df_sm_prec['prec'].plot(secondary_y=True)
plt.gca().invert_yaxis()
ax.set_ylabel(r"Precipitation ($mm/day$)")


# IRRIGATION EVENTS
# calc daily change in sm
df_sm_prec['sm_diff'] = df_sm_prec['sm'] - df_sm_prec['sm'].shift(1)
# register events where sm rises but not due to precipitation
sm_inc_thresh = 0

irrig_events = df_sm_prec[(df_sm_prec['sm_diff'] > sm_inc_thresh) & (df_sm_prec['prec'] == 0.)]
irrig_events['sm_diff'].plot(x='x', y='y', style=".")

plt.title(network + ': ' + station + ' ('+ resampling+')')
plt.show()
