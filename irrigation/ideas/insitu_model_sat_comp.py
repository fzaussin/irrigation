import pandas as pd
import pytesmo.io.ismn.interface as ismn
from pytesmo.time_series.filtering import moving_average
from pytesmo.time_series import anomaly
from pytesmo import temporal_matching
from pytesmo import scaling

from precipitation import trmm_reader
from irrigation.inout import importdata
from irrigation.prep import interp
from irrigation.prep import smooth
from irrigation.comp import slopes
from irrigation.trans import transform

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

# read insitu data
# read ascat, era data
# calc slopes for insitu-model
# calc slopes for ascat-model
# compare with irrig events

# IN SITU
path_to_ismn_data = '/home/fzaussin/shares/users/Irrigation/Data/input/ismn/spain'
ISMN_reader = ismn.ISMN_Interface(path_to_ismn_data)
networks = ISMN_reader.list_networks()
network = networks[0]
stations = ISMN_reader.list_stations(network = network)
# select the irrigated station
station = 'Canizal'
station_obj = ISMN_reader.get_station(station)
#get the variables that this station measures
variables = station_obj.get_variables()
# read sm
sm_depht_from,sm_depht_to = station_obj.get_depths('soil moisture')
sensors = station_obj.get_sensors('soil moisture', sm_depht_from[0],
                                  sm_depht_to[0])

sm = station_obj.read_variable('soil moisture',
                               depth_from=sm_depht_from[0],
                               depth_to=sm_depht_to[0],
                               sensor=sensors[0])

sm_ts_natres = sm.data['soil moisture']
# resample to match model res
sm_ts_6h = sm_ts_natres.resample('6h').mean()
insitu_sm = sm_ts_natres.resample('D').mean()

# TRMM PRECIPITATION
lon_station, lat_station = (-5.35883903503418, 41.195999523)
prec_ts_natres = trmm_reader(lon_station, lat_station)
prec_ts_6h = prec_ts_natres.resample('6h').sum()
prec_ts_1d = prec_ts_natres.resample('D').sum()

# MODELS
nearest_gpi_to_canizal = 755258
era_ts = importdata.era_land_ts(nearest_gpi_to_canizal)

# SATELLITES
data = importdata.QDEGdata().read_gpi(nearest_gpi_to_canizal,
                                      '2007-01-01',
                                      '2013-12-31',
                                      model='eraland',
                                      satellites=['ascat',
                                                  'ascat_reckless_rom',
                                                  'ascat_ultimate_uhnari'])
#fill gaps
data = interp.iter_fill(data, 5)

# add insitu sm and convert to percent
data['insitu'] = insitu_sm * 100
data.dropna(axis=0, how='any', inplace=True)
# unscaled data
#ax1 = data.plot(title='In situ, model and satellite sm data for Canizal station')
#ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
#ax1.set_xlabel('Datetime')

#scaled data
scaled_to_model = scaling.scale(data, 'mean_std', 0)
print scaled_to_model
ax2 = scaled_to_model.plot(title='Scaled to model data')
ax2.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
ax2.set_xlabel('Datetime')

axtrmm = prec_ts_1d.plot()
axtrmm.set_ylabel(r"Precipitation ($mm$)")

# smoothed data
smoothed_data = smooth.iter_movav(scaled_to_model, 35)
ax3 = smoothed_data.plot(title='Data smoothed with 35 day moving average window')
ax3.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
ax3.set_xlabel('Datetime')

axtrmm = prec_ts_1d.plot()
axtrmm.set_ylabel(r"Precipitation ($mm$)")

# SLOPES INSITU - MODEL
slopes_insitu_model = slopes.diffquot_slope_movav(smoothed_data)
psd_insitu_model = slopes.psd(slopes_insitu_model)
psd_monthly = slopes.aggregate_psds(psd_insitu_model, resampling='M')
# plot
ax4 = psd_monthly.plot(kind='bar', title='Monthly PSDS approx. at Canizal Station')
ax4.set_ylabel(r"PSDS ($d^{-1}$)")
ax4.set_xlabel('Datetime')

#psd_insitu_model['insitu'].plot(title='PSD(InSitu, ERA-Land)',
#                                       x='x', y='y', style=".")


# SLOPES ASCAT - MODEL





"""
# INSITU AND MODEL 6 hourly
insitu_model = temporal_matching.matching(era_ts, sm_ts_6h, prec_ts_6h)
insitu_model.rename(columns={'39':'model', 'soil moisture': 'insitu'}, inplace=True)

ax = insitu_model[['model', 'insitu']].plot(title='Insitu vs model sm at Canizal Station (6h)',
                       ylim=(0,1))
ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
ax.set_xlabel('Datetime')

# add pcp
#ax = insitu_model['pcp'].plot(secondary_y=True)
#plt.gca().invert_yaxis()
#ax.set_ylabel(r"Precipitation ($mm/6h$)")
"""

plt.show()
