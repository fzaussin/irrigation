# -*- coding: utf-8 -*-
import numpy as np
import os

from irrigation.trans import transform
from irrigation.prep import timeseries
from irrigation.comp import slopes
from irrigation.prep import interp

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use(['ggplot', 'seaborn-poster'])


def plot_climat_corr(gpi, location=''):
    """
    Plots ASCAT and MERRA SM climatologies with a 35 day rolling correlation
    beneath indicating the general agreement between the two trends.
    :param gpi:
    :return:
    """
    lon, lat = transform.qdeg2lonlat(gpi)

    ts = timeseries.prepare(gpi=gpi,
                 start_date='2007-01-01',
                 end_date='2016-12-31',
                 models=['merra'],
                 satellites=['ascatrecklessrom'],
                 kind='clim')

    # rename cols for manuscript
    ts.rename(columns={'merra': 'MERRA',
                       'ascat_reckless_rom': 'ASCAT'},
              inplace=True)

    # calc rolling correlation
    corr = ts['ASCAT'].rolling(35).corr(ts['MERRA'])

    plt.figure(figsize=(15, 10))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)

    title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                          lat=str(lat),
                                                          lon=str(lon))
    # first row
    ts['MERRA'].plot(ax=ax1, label='MERRA', title=title)  # , ylim=(0.2,0.4))
    ts['ASCAT'].plot(ax=ax1, label='ASCAT')
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

    # second row
    corr.plot(ax=ax2, color='black')
    ax2.set_ylabel("Rolling correlation")
    ax2.set_xlabel("DOY")

    # plot
    plt.tight_layout()
    plt.show()

def plot_movav_corr(gpi, location=''):
    """
    Plots moving averaged satellite and model soil moisture timeseries with a
    rolling correlation (35 day window).
    :param gpi:
    :param location:
    :return:
    """
    lon, lat = transform.qdeg2lonlat(gpi)

    ts = timeseries.prepare(gpi=gpi,
                 start_date='2015-01-01',
                 end_date='2016-12-31',
                 models=['merra'],
                 satellites=['ascatrecklessrom', 'amsr2', 'smapv4am'],
                 kind='movav',
                 window=35)
    # add
    #ts = interp.add_nan(ts)


    # rename cols for manuscript
    ts.rename(columns={'merra': 'MERRA',
                       'ascat_reckless_rom': 'ASCAT',
                       'amsr2': 'AMSR2',
                       'smapv4am': 'SMAP'},
              inplace=True)
    # calc rolling correlation
    ts_model = ts['MERRA']
    ts_sats = ts.drop('MERRA', axis=1)
    corr = ts_model.rolling(35).corr(ts_sats)

    plt.figure(figsize=(15, 10))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)

    title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                          lat=str(lat),
                                                          lon=str(lon))
    # first row
    # TODO: change horrible colorbar!
    ts_model.plot(ax=ax1, title=title, color='black')
    ts_sats.plot(ax=ax1, colormap='Blues_r')

    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

    # second row
    corr.plot(ax=ax2, colormap='Blues_r')
    ax2.set_ylabel("Rolling correlation")
    ax2.set_xlabel("DOY")

    # plot
    plt.tight_layout()
    plt.show()


def climat_slopes_subplot(gpi, location):
    """
    Plots ASCAT and MERRA sm climatologies with daily psd.
    :param gpi:
    :param location:
    :return:
    """
    climat = timeseries.prepare(gpi=gpi,
                                start_date='2007-01-01',
                                end_date='2016-12-31',
                                models=['merra'],
                                satellites=['ascatrecklessrom'],
                                kind='clim')

    # rename cols for manuscript
    climat.rename(columns={'merra': 'MERRA',
                           'ascat_reckless_rom': 'ASCAT'},
                  inplace=True)

    # calc psd
    slopes_climat = slopes.diffquot_slope_climat(climat)
    pos_slope_diffs = slopes.psd(slopes_climat)

    plt.figure(figsize=(12, 7))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)

    lon, lat = transform.qdeg2lonlat(gpi)
    title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                          lat=str(lat),
                                                          lon=str(lon))

    # first row
    climat.plot(ax=ax1, title=title)
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    # second row
    pos_slope_diffs.plot(ax=ax2, kind='line', legend=False, color='darkgrey')

    # fill area under slopes curve
    ax2.fill_between(pos_slope_diffs.index.values, 0,
                     pos_slope_diffs['ASCAT'].values,
                     facecolors='darkgrey')
    ax2.set_ylabel(r"PSD ($d^{-1}$)")
    ax2.set_xlabel("DOY")

    # plot
    plt.tight_layout()
    plt.show()

def climat_slopes_corr_subplot(gpi, location):
    """
    Plots ASCAT and MERRA sm climatologies with daily psd.
    :param gpi:
    :param location:
    :return:
    """
    climat = timeseries.prepare(gpi=gpi,
                                start_date='2007-01-01',
                                end_date='2016-12-31',
                                models=['merra'],
                                satellites=['ascatrecklessrom'],
                                kind='clim')

    # rename cols for manuscript
    climat.rename(columns={'merra': 'MERRA',
                           'ascat_reckless_rom': 'ASCAT'},
                  inplace=True)

    # calc rolling correlation
    ts_model = climat['MERRA']
    ts_sats = climat.drop('MERRA', axis=1)
    corr = ts_model.rolling(35).corr(ts_sats)

    # calc psd
    slopes_climat = slopes.diffquot_slope_climat(climat)
    pos_slope_diffs = slopes.psd(slopes_climat)

    plt.figure(figsize=(15, 8))
    ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
    ax3 = plt.subplot2grid((4, 1), (2, 0), sharex=ax1)
    ax2 = plt.subplot2grid((4, 1), (3, 0), sharex=ax1)

    lon, lat = transform.qdeg2lonlat(gpi)
    title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                          lat=str(lat),
                                                          lon=str(lon))

    # first row
    xticks = [1,30,60,90,120,150,180,210,240,270,300,330,366]
    climat.plot(ax=ax1, title=title, ylim=(0,0.4), xticks=xticks)
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax1.get_yaxis().set_label_coords(-0.07, 0.5)

    # second row
    pos_slope_diffs.plot(ax=ax2, kind='line', legend=False, color='black', ylim=(0, 0.008))
    # fill area under slopes curve
    ax2.fill_between(pos_slope_diffs.index.values, 0,
                     pos_slope_diffs['ASCAT'].values,
                     facecolors='darkgrey')
    ax2.set_ylabel(r"PSD ($d^{-1}$)")
    ax2.set_xlabel("DOY")
    ax2.get_yaxis().set_label_coords(-0.07, 0.5)

    # third row
    corr.plot(ax=ax3, legend=False, color='black')
    ax3.set_ylabel("roll_corr")
    ax3.get_yaxis().set_label_coords(-0.07, 0.5)

    # plot
    plt.tight_layout()
    #plt.show()


if __name__=='__main__':
    # showcase gpis
    loc_dict = {'726000': 'California Central Valley',
                '723239': 'Mississippi Delta',
                '763461': 'Snake River Valley, Idaho',
                '750568': 'Plains of Nebraska',
                '701663': 'Georgia'}

    out_dir = '/home/fzaussin/TIMESERIES/NEW'
    id = 'climat_corr_psd_'
    for gpi, loc in loc_dict.iteritems():
        climat_slopes_corr_subplot(int(gpi), loc)
        plt.savefig(os.path.join(out_dir, id + loc),
                    format='pdf',
                    dpi=300)
