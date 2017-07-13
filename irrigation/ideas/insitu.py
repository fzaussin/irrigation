import pytesmo.io.ismn.interface as ismn
from pytesmo.validation_framework import temporal_matchers
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks", context='poster')
import random
from irrigation.trans import transform
from pytesmo.time_series.filtering import moving_average

#path unzipped file downloaded from the ISMN web portal
#path_to_ismn_data = '/home/fzaussin/shares/users/Irrigation/Data/input/ismn'
path_to_ismn_data = '/home/fzaussin/shares/users/Irrigation/Data/input/ismn/texas'

#initialize interface, this can take up to a few minutes the first
#time, since all metadata has to be collected
ISMN_reader = ismn.ISMN_Interface(path_to_ismn_data)

#select random network and station to plot
networks = ISMN_reader.list_networks()
print "Available Networks:"
print networks

# loop through networks and stations
for network in networks:
    stations = ISMN_reader.list_stations(network = network)
    print "Available Stations in Network %s"%network
    print stations

    for station in stations:

        # loop through all stations and create irrig events plots
        station_obj = ISMN_reader.get_station(station)
        print "Available Variables at Station %s"%station
        #get the variables that this station measures
        variables = station_obj.get_variables()
        print 'variables: ', variables

        #to make sure the selected variable is not measured
        #by different sensors at the same depths
        #we also select the first depth and the first sensor
        #even if there is only one
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
        #ax=sm.plot(ylim=(0,1), legend=True)
        #ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

        # PRECIPITATION
        try:
            prec_depth_from,prec_depth_to = station_obj.get_depths('precipitation')
            print prec_depth_from,prec_depth_to
            prec = station_obj.read_variable('precipitation',depth_from=prec_depth_from[0],depth_to=prec_depth_to[0])
        except TypeError:
            print 'No prec data available'
            continue
       # ax = prec.plot(secondary_y=True, legend=True)
        #plt.gca().invert_yaxis()
        #ax.set_ylabel(r"Precipitation ($mm/day$)")



        # IRRIGATION EVENTS
        sm_ts = sm.data['soil moisture']
        prec_ts = prec.data['precipitation']
        # resample to daily res
        sm_ts = sm_ts.resample('D').mean()
        prec_ts = prec_ts.resample('D').sum()
        # combine to df
        df_sm_prec = pd.DataFrame(index=sm_ts.index)
        df_sm_prec['sm'] = sm_ts
        df_sm_prec['prec'] = prec_ts

        ax = df_sm_prec['sm'].plot(ylim=(0,1))
        ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

        ax = df_sm_prec['prec'].plot(secondary_y=True)
        plt.gca().invert_yaxis()
        ax.set_ylabel(r"Precipitation ($mm/day$)")


        # plot sm and prec
        #ax = df_sm_prec.plot(secondary_y=['prec'], title="test")
        #ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
        #ax.right_ax.set_ylabel(r"Precipitation ($mm/day$)")

        # calc daily change in sm
        df_sm_prec['sm_diff'] = df_sm_prec['sm'] - df_sm_prec['sm'].shift(1)
        # register events where sm rises but not due to precipitation
        sm_inc_thresh = 0

        irrig_events = df_sm_prec[(df_sm_prec['sm_diff'] > sm_inc_thresh) & (df_sm_prec['prec'] == 0.)]
        irrig_events['sm_diff'].plot(x='x', y='y', style=".")

        plt.title(network + ': ' + station)
        plt.show()
        """
        fpath = os.path.join('/home/fzaussin/Desktop/ismn/v2',
                             network + '_' + station)
        plt.savefig(fpath, dpi=200, figsize=(20,15))
        plt.close()
        """

    """
    INFO

    SCAN:
        BeasleyLake: probably irrigated
        GoodwinCreekPasture: not irrigated
        GoodwinCreekTimber: nI
        NorthIssaquena: I
        Perthshire: I
        SandyRidge: I
        Scott: I
        SilverCity: pI
        Tunica: I
        UAPBCampus-PB: nI
        UAPBLonokeFarm: pI
        UAPBMarianna: I
    """