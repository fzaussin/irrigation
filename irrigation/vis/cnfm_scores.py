# force floating point division
from __future__ import division

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn import metrics


def psds2binary(path, threshhold=10):
    """
    Create binary psds map based on threshold. For validation with mirad-us.
    :param path:
    :param threshhold:
    :return:
    """
    psds = pd.DataFrame.from_csv(path)
    # set threshold to >= 10
    psds[psds < threshhold] = 0.0
    psds[psds >= threshhold] = 1.0
    psds['gpi_quarter'] = psds.index.values
    binary_psds = psds.fillna(0)
    return binary_psds

def align_with_mirad(binary_psds):
    """
    Align psds data to mirad data to create one df holding psds over time and
    the irrig_fraction, because confusion_matrix needs input of same length.
    :param psds_data:
    :return:
    """
    mirad = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/validation/mirad_downscaling/mirad-25km/BINARY_thresh>=5_mirad25kmv2_lat_lon_gpi_025degrees.csv')
    merged_data = pd.merge(binary_psds, mirad, how='left',
                           on='gpi_quarter')
    return merged_data


def return_subset(merged_data, bbox):
    min_lon, min_lat, max_lon, max_lat = bbox
    data = merged_data.loc[(merged_data.lon <= max_lon) &
                           (merged_data.lon >= min_lon) &
                           (merged_data.lat <= max_lat) &
                           (merged_data.lat >= min_lat)]

    data.drop(['lon', 'lat', 'gpi_quarter'], axis=1, inplace=True)
    return data


def cnfm_scores(y_true, y_pred):
    """Compute error matrix summary for binary classification."""
    cnf_matrix = metrics.confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cnf_matrix.ravel()

    # build dictionary with scores
    summary = {}
    # Producers accuracy
    summary['PA_I'] = tp / (tp + fn)
    summary['PA_NI'] = tn / (tn + fp)
    # Users accuracy
    summary['UA_I'] = tp / (tp + fp)
    summary['UA_NI'] = tn / (tn + fn)
    # Error of Comission
    summary['EoC_I'] = fp / (tp + fp)
    summary['EoC_NI'] = fn / (tn + fn)
    # Error of Ommission
    summary['EoO_I'] = fn / (tp + fn)
    summary['EoO_NI'] = fp / (tn + fp)
    # Overall accuracy
    summary['Accuracy'] = (tp + tn) / (tp + tn + fp + fn)
    # kappa score
    summary['Kappa'] = metrics.cohen_kappa_score(y_true, y_pred)

    return summary


def return_merged(path, threshold=0.04):
    """Convert psds to binary based on thresh and merge with mirad"""
    binary_psds = psds2binary(path, threshold)
    merged_data = align_with_mirad(binary_psds)

    # rename for consistency
    merged_data.rename(columns={'April': 'Apr',
                                'June': 'Jun',
                                'July': 'Jul',
                                'September': 'Sep',
                                'October': 'Oct'}, inplace=True)
    return merged_data

def bbox_scores(merged_data, bbox):
    """Compute cnfm scores for specified bounding box"""
    subset = return_subset(merged_data, bbox)

    # mirad is considered ground truth
    y_true = subset['irrigation'].values
    psds = subset.drop('irrigation', axis=1)

    # container to store scores for each time period
    d = {}
    for time_agg in psds:
        # psds per month
        y_pred = psds[time_agg].values
        # compute scores and append to dict
        scores = cnfm_scores(y_true, y_pred)
        d[time_agg] = scores

    # create df from dict, transpose to have time as index and sort periods
    df_scores = pd.DataFrame.from_dict(d)
    df_scores = df_scores.transpose()
    return df_scores

def plot_scores(df_scores, title=''):
    """Plots obtained scores as 4 subplots over time."""

    df_scores = df_scores.reindex(['Apr', 'May', 'Jun', 'Jul',
                                   'Aug', 'Sep',
                                   'Oct'])

    # rename columns once to get nice legends
    df_scores.rename(columns={'EoC_I': 'Error of commission',
                              'EoO_I': 'Error of ommission',
                              'PA_I': "Producer's accuracy",
                              'UA_I': "User's accuracy",
                              'Accuracy': 'Overall accuracy',
                              'Kappa': "Kappa statistic"}, inplace=True)
    print df_scores

    fig = plt.figure(figsize=(12, 8))
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((6, 1), (2, 0), sharex=ax1, sharey=ax1, rowspan=2)
    ax3 = plt.subplot2grid((6, 1), (4, 0), sharex=ax1, sharey=ax1, rowspan=2)

    # Plots only the IRRIGATED CLASS SCORES (!)
    # Errors
    df_scores[['Error of commission', 'Error of ommission']].plot.bar(ax=ax1, title=title, color=['#993404', '#fe9929'], legend=False, ylim=(0,1))
    # Accuracies
    df_scores[["Producer's accuracy", "User's accuracy"]].plot.bar(ax=ax2, color=['#006837', '#78c679'], legend=False, ylim=(0,1))
    # Overall accuracy and kappa
    df_scores[['Overall accuracy', "Kappa statistic"]].plot.bar(ax=ax3, color=['#3182bd', '#636363'], legend=False, ylim=(-0.25,1))

    # labels to the right
    ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax3.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    # set the xaxis label
    plt.setp(ax3.xaxis.get_label(), visible=True)
    # set the ticks
    plt.setp(ax3.get_xticklabels(), visible=True, rotation=0)
    plt.tight_layout()
    #fig.subplots_adjust(right=0.7)

def plot_scores_movav(df_scores, title=''):
    """Plots obtained scores as 4 subplots over time."""

    # rename columns once to get nice legends
    df_scores.rename(columns={'EoC_I': 'Error of commission',
                              'EoO_I': 'Error of ommission',
                              'PA_I': "Producer's accuracy",
                              'UA_I': "User's accuracy",
                              'Accuracy': 'Overall accuracy',
                              'Kappa': "Kappa statistic"}, inplace=True)
    print df_scores

    fig = plt.figure(figsize=(12, 8))
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((6, 1), (2, 0), sharex=ax1, sharey=ax1, rowspan=2)
    ax3 = plt.subplot2grid((6, 1), (4, 0), sharex=ax1, sharey=ax1, rowspan=2)

    # Plots only the IRRIGATED CLASS SCORES (!)
    # Errors
    df_scores[['Error of commission', 'Error of ommission']].plot.bar(ax=ax1, title=title, color=['#993404', '#fe9929'], legend=False, ylim=(0,1))
    # Accuracies
    df_scores[["Producer's accuracy", "User's accuracy"]].plot.bar(ax=ax2, color=['#006837', '#78c679'], legend=False, ylim=(0,1))
    # Overall accuracy and kappa
    df_scores[['Overall accuracy', "Kappa statistic"]].plot.bar(ax=ax3, color=['#3182bd', '#636363'], legend=False, ylim=(-0.25,1))

    # labels to the right
    ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax3.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    # change index to only display year and month in plot
    df_scores.index = pd.to_datetime(df_scores.index)
    tstamps = df_scores.index
    format_tstamps = tstamps.map(lambda t: t.strftime('%Y-%m'))
    ax3.set_xticklabels(format_tstamps)

    # set the xaxis label
    plt.setp(ax3.xaxis.get_label(), visible=True)
    # set the ticks
    plt.setp(ax3.get_xticklabels(), visible=True, rotation=90)
    plt.tight_layout()
    #fig.subplots_adjust(right=0.7)

if __name__== '__main__':
    import os
    import matplotlib
    matplotlib.style.use(['ggplot', 'seaborn-poster'])

    bboxes = {'USA': (-125, 24, -65, 50),
         'California': (-124.48, 32.53, -114.13, 42.01),
         'Nebraska': (-104.05,40.00,-95.31,43.00),
         'Georgia': (-85.61,30.36,-80.75,35.00),
         'Mississippi': (-92.36, 31.21,-88.98,37.61)}


    # create conf-matrix bar plot for climats
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/seasonal_merra_smapv4am_2015-01-01_2016-12-31.csv'
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/seasonal_merra_ascatrecklessrom_2015-01-01_2016-12-31.csv'
    path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/climatology-based/ascat-merra-climat-based-months.csv'

    # tresh
    thresh = 0.04

    # merge with mirad
    merged_data = return_merged(path, thresh)

    # for one bbox
    #df_scores = bbox_scores(merged_data, bboxes['California'])
    #plot_scores_movav(df_scores, title='California')
    #plt.show()


    out_dir = '/home/fzaussin/Desktop/cnfm-scores/seasonal-movav/'
    # bbox subset
    for region, bbox in bboxes.iteritems():
        print region, bbox
        df_scores = bbox_scores(merged_data, bbox)
        df_scores.to_csv('/home/fzaussin/Desktop/cnfm-scores/monthly-climats/' + region + '.csv')

        """
        plot_scores_movav(df_scores, title=region)

        print df_scores
        outpath = out_dir + 'seasonal-amsr2-' + region + '.pdf'
        plt.savefig(outpath,
                    format='pdf')


    # df_scores.to_csv(
    #    '/home/fzaussin/Desktop/cnfm-scores/seasonal-movav/seasonal-scores-amsr2-' + region + '.csv')
        """