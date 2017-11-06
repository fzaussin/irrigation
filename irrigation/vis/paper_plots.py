# -*- coding: utf-8 -*-
import numpy as np
import os

from irrigation.trans import transform
from irrigation.prep import timeseries
from irrigation.comp import slopes
from irrigation.prep import interp

from pytesmo.time_series import anomaly
from rsdata.GPCC.interface import GpccFirstGuessDailyTs

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import matplotlib
matplotlib.style.use(['ggplot', 'seaborn-poster'])


def plot_climat_corr(gpi, location='', show=True):
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
    ts['MERRA'].plot(ax=ax1, label='MERRA', title=title, ylim=(0.15,0.4))
    ts['ASCAT'].plot(ax=ax1, label='ASCAT')
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")

    # second row
    corr.plot(ax=ax2, color='black')
    ax2.set_ylabel("Rolling correlation")
    ax2.set_xlabel("DOY")

    # plot
    plt.tight_layout()
    if show:
        plt.show()
    else:
        pass

def plot_movav_corr(gpi, location='', show=True):
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
    if show:
        plt.show()
    else:
        pass

def climat_slopes_subplot(gpi, location='', show=True):
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
                           'ascatrecklessrom': 'ASCAT'},
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
    xticks = [1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 366]
    climat.plot(ax=ax1, title=title, xticks=xticks, ylim=(0.15,0.4))
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax1.get_yaxis().set_label_coords(-0.1, 0.5)
    # second row
    pos_slope_diffs.plot(ax=ax2, kind='line', legend=False, color='black', ylim=(0,0.007))
    # sum for May-September (leap year doy calendar)
    yearly_psds = pos_slope_diffs[122:274].sum()['ASCAT']
    # add to plot as textbox
    textstr = "PSDS = {:2.3f}".format(yearly_psds) + r" $d^{-1}$"
    anchored_text = AnchoredText(textstr, loc=2, frameon=True, prop=dict(size=12))
    anchored_text.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax2.add_artist(anchored_text)

    # fill area under slopes curve
    ax2.fill_between(pos_slope_diffs.index.values, 0,
                     pos_slope_diffs['ASCAT'].values,
                     facecolors='darkgrey')
    ax2.set_ylabel(r"PSD ($d^{-1}$)")
    ax2.set_xlabel("DOY")
    ax2.get_yaxis().set_label_coords(-0.1, 0.5)

    # plot
    plt.tight_layout()
    if show:
        plt.show()
    else:
        pass

def climat_slopes_prec_subplot(gpi, location='', show=True):
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
                                satellites=['ascatrecklessrom', 'amsr2', 'smap'],
                                kind='clim')

    # rename cols for manuscript
    climat.rename(columns={'merra': 'MERRA',
                           'ascatrecklessrom': 'ASCAT'},
                  inplace=True)
    # convert gpi to lon lat
    lon, lat = transform.qdeg2lonlat(gpi)

    # calc prec climat
    gpcc = GpccFirstGuessDailyTs().read_ts(lon, lat)['prec']
    gpcc_climat = anomaly.calc_climatology(gpcc, moving_avg_clim=70, wraparound=True)

    # calc psd
    slopes_climat = slopes.diffquot_slope_climat(climat)
    pos_slope_diffs = slopes.psd(slopes_climat)


    # create figure
    plt.figure(figsize=(12, 7))
    ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
    ax3 = plt.subplot2grid((4, 1), (2, 0), sharex=ax1)
    ax2 = plt.subplot2grid((4, 1), (3, 0), sharex=ax1)

    # define SOS and EOS
    # for missouri computed with excel
    cc_mean_planting = 119
    cc_mean_harvesting = 308

    # take minimum and maximum values of the most active planting and
    # harvesting periods to define sos and eos ranges
    # -> eliminates outliers
    planting_min = 102
    planting_max = 134
    harvesting_min = 292
    harvesting_max = 314

    # lightely shaded
    min_max_planting = range(planting_min, planting_max + 1)
    min_max_harvesting = range(harvesting_min, harvesting_max + 1)
    # darkely shaded
    left_oos = range(1, planting_min + 1)
    right_oos = range(harvesting_max, 367)

    # shade colors
    color_oos = 'darkgrey'
    alpha_oos = 0.9
    color_min_max = 'lightgrey'
    alpha_min_max = 0.8

    # mean planting and harvesting marked by vertical lines
    ax1.plot((cc_mean_planting, cc_mean_planting), (0, 10), color='grey',
             linestyle='dotted')
    ax1.plot((cc_mean_harvesting, cc_mean_harvesting), (0, 10), color='grey',
             linestyle='dotted')
    ax2.plot((cc_mean_planting, cc_mean_planting), (0, 10), color='grey',
             linestyle='dotted')
    ax2.plot((cc_mean_harvesting, cc_mean_harvesting), (0, 10), color='grey',
             linestyle='dotted')
    ax3.plot((cc_mean_planting, cc_mean_planting), (0, 10), color='grey',
             linestyle='dotted')
    ax3.plot((cc_mean_harvesting, cc_mean_harvesting), (0, 10), color='grey',
             linestyle='dotted')

    # fill axes
    ax1.fill_between(left_oos, 0, np.repeat(10, len(left_oos)),
                     facecolors=color_oos, alpha=alpha_oos)
    ax1.fill_between(min_max_planting, 0, np.repeat(10, len(min_max_planting)),
                     facecolors=color_min_max, alpha=alpha_min_max)
    ax1.fill_between(min_max_harvesting, 0,
                     np.repeat(10, len(min_max_harvesting)),
                     facecolors=color_min_max, alpha=alpha_min_max)
    ax1.fill_between(right_oos, 0, np.repeat(10, len(right_oos)),
                     facecolors=color_oos, alpha=alpha_oos)

    ax2.fill_between(left_oos, 0, np.repeat(10, len(left_oos)),
                     facecolors=color_oos, alpha=alpha_oos)
    ax2.fill_between(min_max_planting, 0, np.repeat(10, len(min_max_planting)),
                     facecolors=color_min_max, alpha=alpha_min_max)
    ax2.fill_between(min_max_harvesting, 0,
                     np.repeat(10, len(min_max_harvesting)),
                     facecolors=color_min_max, alpha=alpha_min_max)
    ax2.fill_between(right_oos, 0, np.repeat(10, len(right_oos)),
                     facecolors=color_oos, alpha=alpha_oos)

    ax3.fill_between(left_oos, 0, np.repeat(10, len(left_oos)),
                     facecolors=color_oos, alpha=alpha_oos)
    ax3.fill_between(min_max_planting, 0, np.repeat(10, len(min_max_planting)),
                     facecolors=color_min_max, alpha=alpha_min_max)
    ax3.fill_between(min_max_harvesting, 0,
                     np.repeat(10, len(min_max_harvesting)),
                     facecolors=color_min_max, alpha=alpha_min_max)
    ax3.fill_between(right_oos, 0, np.repeat(10, len(right_oos)),
                     facecolors=color_oos, alpha=alpha_oos)

    # make title
    title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                          lat=str(lat),
                                                          lon=str(lon))

    # SOIL MOISTURE
    xticks = [1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 366]
    climat.plot(ax=ax1, title=title, xticks=xticks, ylim=(0,0.45)) #, ylim=(0.15,0.4)
    ax1.legend(loc=3)
    ax1.set_ylabel("Soil moisture \n" + r"($m^{3} m^{-3}$)")
    ax1.get_yaxis().set_label_coords(-0.1, 0.5)

    # PRECIPITATION
    gpcc_climat.plot(ax=ax3, color='black', ylim=(0,5)) #, ylim=(2.75, 5.25)
    # r"Precipitation \n ($mm d^{-1}$)"
    ax3.set_ylabel("Rainfall \n" + r"($mm\/d^{-1}$)")
    ax3.get_yaxis().set_label_coords(-0.1, 0.5)

    # PSD
    pos_slope_diffs.plot(ax=ax2, kind='line', legend=False, color='black', ylim=(0,0.01))
    # make line over fill of psd thinner
    ax2.lines[-1].set_linewidth(2)
    # sum for May-September (leap year doy calendar)
    yearly_psds = pos_slope_diffs[cc_mean_planting:cc_mean_harvesting].sum()['ASCAT']
    # add to plot as textbox
    textstr = "PSDS = {:2.3f}".format(yearly_psds) + r" $d^{-1}$"
    anchored_text = AnchoredText(textstr, loc=2, frameon=True, prop=dict(size=12))
    anchored_text.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax2.add_artist(anchored_text)

    # fill area under slopes curve
    ax2.fill_between(pos_slope_diffs.index.values, 0,
                     pos_slope_diffs['ASCAT'].values,
                     facecolors='#c6dbef')
    ax2.set_ylabel("PSD \n" + r"($d^{-1}$)")
    ax2.set_xlabel("DOY")
    ax2.get_yaxis().set_label_coords(-0.1, 0.5)

    """
    # shade everything outside the approx. growing season
    sos = 137
    eos = 274

    # calculate doy ranges
    before_season = range(1, sos + 1)
    after_season = range(eos + 1, 367)

    # repeat for each axis
    ax1.fill_between(before_season, 0, np.repeat(10, len(before_season)),
                     facecolors='darkgrey', alpha=0.7)
    ax1.fill_between(after_season, 0, np.repeat(10, len(after_season)),
                     facecolors='darkgrey', alpha=0.7)
    ax2.fill_between(before_season, 0, np.repeat(10, len(before_season)),
                     facecolors='darkgrey', alpha=0.7)
    ax2.fill_between(after_season, 0, np.repeat(10, len(after_season)),
                     facecolors='darkgrey', alpha=0.7)
    ax3.fill_between(before_season, 0, np.repeat(10, len(before_season)),
                     facecolors='darkgrey', alpha=0.7)
    ax3.fill_between(after_season, 0, np.repeat(10, len(after_season)),
                     facecolors='darkgrey', alpha=0.7)
    """




    # plot
    plt.tight_layout()
    if show:
        plt.show()
    else:
        pass

def climat_slopes_corr_subplot(gpi, location, show=True):
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
                           'ascatrecklessrom': 'ASCAT'},
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
    climat.plot(ax=ax1, title=title, xticks=xticks) # ylim=(0.15,0.4),
    ax1.legend(loc=3)
    ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
    ax1.get_yaxis().set_label_coords(-0.07, 0.5)

    # second row
    pos_slope_diffs.plot(ax=ax2, kind='line', legend=False, color='black') # , ylim=(0, 0.01)
    ax2.lines.set_linewidth(1)
    # sum for May-September (leap year doy calendar)
    yearly_psds = pos_slope_diffs[122:274].sum()['ASCAT']
    # add to plot as textbox
    textstr = "PSDS = {:2.3f}".format(yearly_psds) + r" $d^{-1}$"
    anchored_text = AnchoredText(textstr, loc=2, frameon=True,
                                 prop=dict(size=12))
    anchored_text.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax2.add_artist(anchored_text)

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
    if show:
        plt.show()
    else:
        pass


if __name__=='__main__':
    climat_slopes_prec_subplot(753440)
    plt.show()

    """
    # showcase gpis
    loc_dict = {'726000': 'California Central Valley',
                '723239': 'Mississippi Delta',
                '763461': 'Snake River Valley, Idaho',
                '750568': 'Plains of Nebraska',
                '701663': 'Georgia'}
    #id = 'psd_rollingcorr_'

    irrig_dict = {'730442': 'Irrigated',
                  '730443': 'Half irrigated',
                  '730444': 'Partially irrigated',
                  '730445': 'Rainfed'}
    id = 'psd_comp_'
    out_dir = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/'


    for gpi, loc in irrig_dict.iteritems():
        print loc
        climat_slopes_prec_subplot(int(gpi), loc, show=True)

        plt.savefig(os.path.join(out_dir, id + loc + '.pdf'),
                    format='pdf',
                    dpi=300)
    """