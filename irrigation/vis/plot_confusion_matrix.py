"""
================
Confusion matrix
================

Example of confusion matrix usage to evaluate the quality
of the output of a classifier on the iris data set. The
diagonal elements represent the number of points for which
the predicted label is equal to the true label, while
off-diagonal elements are those that are mislabeled by the
classifier. The higher the diagonal values of the confusion
matrix the better, indicating many correct predictions.

The figures show the confusion matrix with and without
normalization by class support size (number of elements
in each class). This kind of normalization can be
interesting in case of class imbalance to have a more
visual interpretation of which class is being misclassified.

Here the results are not as good as they could be as our
choice for the regularization parameter C was not the best.
In real life applications this parameter is usually chosen
using :ref:`grid_search`.

"""

# force floating point division
from __future__ import division

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix
from sklearn import metrics

from matplotlib.colors import ListedColormap
from irrigation.vis.spatialplot import spatial_plot_quarter_grid


def plot_confusion_matrix(cm, classes,
                          normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    #This function prints and plots the confusion matrix.
    #Normalization can be applied by setting `normalize=True`.
    """
    print cm
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm = np.round(cm, 2)
        print cm, type(cm)
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 #color='black')
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('MIrAD-US')
    plt.xlabel('PSDS')


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

def cnfm_scores(y_true, y_pred):
    """Compute error matrix summary for binary classification."""
    cnf_matrix = metrics.confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cnf_matrix.ravel()
    print (tn, fp, fn, tp)

    # build dictionary with scores
    summary = {}
    # Producers accuracy
    summary['PA'] = tp / (tp + fn)
    # Users accuracy
    summary['UA'] = tp / (tp + fp)
    # Error of Comission
    summary['EoC'] = fp / (tp + fp)
    # Error of Ommission
    summary['EoO'] = fn / (tp + fn)
    # Overall accuracy
    summary['overall_accuracy'] = (tp + tn) / (tp + tn + fp + fn)
    # kappa score
    summary['kappa'] = metrics.cohen_kappa_score(y_true, y_pred)

    return summary



def iter_conf_matrix(merged_data, show=False):
    """
    Iterate over aggregated psds and create conf matrix with mirad-us.
    Row-wise normalization yields 100% for TN and FP / 100% for FN and TP
    :param merged_data:
    :return:
    """
    mirad = merged_data['irrigation'].values
    psds_agg = merged_data.drop('irrigation', axis=1)

    cnf_matrix_dict = {}

    for time_agg in psds_agg:
        y_true = mirad
        y_pred = psds_agg[time_agg].values
        # confusion matrix
        cnf_matrix = confusion_matrix(y_true, y_pred)

        ### Some additional scores for interpretation
        # also compute kappa score and print
        kappa = metrics.cohen_kappa_score(y_true, y_pred)
        # overall accuracy = (tp + tn) / (tp + tn + fp + fn)
        overall_accuracy = metrics.accuracy_score(y_true, y_pred)
        print '    {time}: kappa = {kappa}, overall accuracy sklearn = {acc}'.format(time=time_agg, kappa=kappa, acc=overall_accuracy)
        ###

        # normalize and append to dict
        cm_norm = cnf_matrix.astype('float') / cnf_matrix.sum(axis=1)[:, np.newaxis]
        #cm_norm = np.round(cm_norm, 2)
        cnf_matrix_dict[time_agg] = cm_norm.flatten()

        # plot
        """
        plt.figure()
        plot_confusion_matrix(cnf_matrix,
                              classes=['non-irrigated', 'irrigated'],
                              normalize=True,
                              title='Normalized confusion matrix for {}'.format(time_agg))
        """
    if show:
        plt.show()
    else:
        return cnf_matrix_dict

def return_subset(merged_data, bbox):
    min_lon, min_lat, max_lon, max_lat = bbox
    data = merged_data.loc[(merged_data.lon <= max_lon) &
                           (merged_data.lon >= min_lon) &
                           (merged_data.lat <= max_lat) &
                           (merged_data.lat >= min_lat)]

    data.drop(['lon', 'lat', 'gpi_quarter'], axis=1, inplace=True)
    return data


def cnfm_over_time_climats(merged_data, bbox=None, region='', show=True):
    """
    Creates bar plot of confusion matrix over time for a specific region or
    the whole input data frame.
    :param df:
    :param bbox: tuple
        (min_lon, min_lat, max_lon, max_lat)
    :param region:
    :return:
    """
    if bbox is not None:
        min_lon, min_lat, max_lon, max_lat = bbox
        data = merged_data.loc[(merged_data.lon <= max_lon) &
                               (merged_data.lon >= min_lon) &
                               (merged_data.lat <= max_lat) &
                               (merged_data.lat >= min_lat)]

    data.drop(['lon', 'lat', 'gpi_quarter'], axis=1, inplace=True)

    cnf_dict = iter_conf_matrix(data)
    print cnf_dict

    # stack confusion matrices over time in df
    df = pd.DataFrame.from_dict(cnf_dict)
    # rename august
    df.rename(columns={'Aug': 'August'}, inplace=True)
    # transpose and rename new columns
    cnfm_over_time = df.transpose()
    cnfm_over_time.rename(columns={0: 'TN',
                                   1: 'FP',
                                   2: 'FN',
                                   3: 'TP'}, inplace=True)
    # reorder columns and rows
    cnfm_over_time = cnfm_over_time[['TP', 'FN', 'TN', 'FP']]
    cnfm_over_time = cnfm_over_time.reindex(['April', 'May', 'June', 'July',
                                             'August', 'September',
                                             'October'])
    # transform to % between [0, 100]
    cnfm_over_time = cnfm_over_time.multiply(100)

    # save exact values to csv
    outdir = '/home/fzaussin/Desktop/cnfm-scores/monthly-climats/Mississippi.pdf'
    cnfm_over_time.to_csv(outdir + region + '.csv')

    # create barplot with custom colors
    plt.figure(figsize=(12, 8))
    ax1 = plt.subplot2grid((2, 1), (0, 0))
    ax2 = plt.subplot2grid((2, 1), (1, 0), sharex=ax1, sharey=ax1)


    cnfm_over_time[['TN', 'FP']].plot.bar(ax=ax1, color=['#80cdc1', '#a6611a'],
                                          stacked=True, ylim=(0, 100),
                                          alpha=0.7, legend=False, title=region)
    cnfm_over_time[['TP', 'FN']].plot.bar(ax=ax2, color=['#018571', '#dfc27d'],
                                          stacked=True, ylim=(0, 100),
                                          alpha=0.7, legend=False)

    ax1.set_ylabel('Percent (%)')
    ax2.set_ylabel('Percent (%)')

    ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    plt.tight_layout()
    if show:
        plt.show()

def cnfm_over_time_movav(merged_data, bbox=None, region='', show=True):
    """
    Creates bar plot of confusion matrix over time for a specific region or
    the whole input data frame.
    :param df:
    :param bbox: tuple
        (min_lon, min_lat, max_lon, max_lat)
    :param region:
    :return:
    """
    if bbox is not None:
        min_lon, min_lat, max_lon, max_lat = bbox
        data = merged_data.loc[(merged_data.lon <= max_lon) &
                               (merged_data.lon >= min_lon) &
                               (merged_data.lat <= max_lat) &
                               (merged_data.lat >= min_lat)]

    data.drop(['lon', 'lat', 'gpi_quarter'], axis=1, inplace=True)

    cnf_dict = iter_conf_matrix(data)

    # stack confusion matrices over time in df
    df = pd.DataFrame.from_dict(cnf_dict)
    # transpose and rename new columns
    cnfm_over_time = df.transpose()
    cnfm_over_time.rename(columns={0: 'TN',
                                   1: 'FP',
                                   2: 'FN',
                                   3: 'TP'}, inplace=True)
    # reorder columns
    cnfm_over_time = cnfm_over_time[['TP', 'FN', 'TN', 'FP']]

    # transform to % between [0, 100]
    cnfm_over_time = cnfm_over_time.multiply(100)

    # save exact values to csv
    outdir = '/home/fzaussin/Desktop/cnfm-scores/monthly-climats/'
    #cnfm_over_time.to_csv(outdir + 'monthly_' + region + '.csv')
    cnfm_over_time.to_csv(outdir + 'climat_' + region + '.csv')

    # create barplot with custom colors

    # change index to only display year and month in plot
    cnfm_over_time.index = pd.to_datetime(cnfm_over_time.index)
    tstamps = cnfm_over_time.index
    format_tstamps = tstamps.map(lambda t: t.strftime('%Y-%m'))

    """
    # create plot
    ax = cnfm_over_time.plot.bar(
        color=['#018571', '#dfc27d', '#80cdc1', '#a6611a'],
        title=title, stacked=True, ylim=(0, 200), alpha=0.7)
    ax.set_ylabel('Percent (%)')
    ax.set_xticklabels(format_tstamps)
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    """

    # create barplot with custom colors
    plt.figure(figsize=(12, 8))
    ax1 = plt.subplot2grid((2, 1), (0, 0))
    ax2 = plt.subplot2grid((2, 1), (1, 0), sharex=ax1, sharey=ax1)


    cnfm_over_time[['TN', 'FP']].plot.bar(ax=ax1, color=['#80cdc1', '#a6611a'],
                                          stacked=True, ylim=(0, 100),
                                          alpha=0.7, legend=False, title=region)
    cnfm_over_time[['TP', 'FN']].plot.bar(ax=ax2, color=['#018571', '#dfc27d'],
                                          stacked=True, ylim=(0, 100),
                                          alpha=0.7, legend=False)

    ax1.set_ylabel('Percent (%)')
    ax2.set_ylabel('Percent (%)')

    ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    ax2.set_xticklabels(format_tstamps)

    plt.tight_layout()
    if show:
        plt.show()

def binary_map(path, show=True, thresh=0):
    """Plots binary irrigation map"""

    binary_psds = psds2binary(path, thresh)
    merged_data = align_with_mirad(binary_psds)

    # create plot
    cmap_binary = ListedColormap(['#f2f2f2', '#045a8d'], 'indexed')

    if show:
        spatial_plot_quarter_grid(merged_data, title='tag', cbar=False,
                                  cmap=cmap_binary)
    else:
        dir = os.path.split(path)[0]
        fname = os.path.split(path)[1]
        region, mod, sat = fname.split('_')[:3]

        spatial_plot_quarter_grid(merged_data, title='tag', cbar=False,
                                  cmap=cmap_binary,
                                  path=dir,
                                  fname='binary_{}_{}_{}'.format(thresh, mod, sat))

def unwrap_path(path):
    dir = os.path.split(path)[0]
    fname = os.path.split(path)[1]
    region, mod, sat = fname.split('_')[:3]
    return region, mod, sat

if __name__== '__main__':
    import os
    from irrigation.vis import spatialplot
    import matplotlib
    matplotlib.style.use(['ggplot', 'seaborn-poster'])

    bboxes = {'USA': (-125, 24, -65, 50),
         'California': (-124.48, 32.53, -114.13, 42.01),
         'Nebraska': (-104.05,40.00,-95.31,43.00),
         'Georgia': (-85.61,30.36,-80.75,35.00),
         'Mississippi': (-92.36, 31.21,-88.98,37.61)}

    path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/FIXED/movav-based/smapv4_mean/seasonal_merra_smapv4_2015-01-01_2016-12-31.csv'

    binary_map(path, show=False, thresh=0.08)
    #plt.show()

    """
    # create conf-matrix bar plot for climats
    path_climat = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/climatology-based/ascat-merra-climat-based-months.csv'

    thresh = 0.04
    binary_psds = psds2binary(path_climat, thresh)
    merged_data = align_with_mirad(binary_psds)


    out_dir = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/conf-matrix-final/climats-classification/'
    for region, bbox in bboxes.iteritems():
        print region, bbox
        cnfm_over_time_climats(merged_data, bbox, show=False,
                             region="{} {}".format(region, str(bbox)))

        plt.savefig(os.path.join(out_dir, region + '.pdf'),
                    dpi=300,
                    bbox_inches='tight',
                    format='pdf')



    # conf matrix over time for movav

    temp_res = 'monthly'
    # make psds and mirad binary based on thresh

    # SMAP
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/monthly_merra_smapv4am_2015-01-01_2016-12-31.csv'
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/seasonal_merra_smapv4am_2015-01-01_2016-12-31.csv'

    # ASCAT
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/monthly_merra_ascatrecklessrom_2015-01-01_2016-12-31.csv'
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/seasonal_merra_ascatrecklessrom_2015-01-01_2016-12-31.csv'

    # AMSR-2
    #path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/monthly_merra_amsr2_2015-01-01_2016-12-31.csv'
    path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/movav-based/seasonal_merra_amsr2_2015-01-01_2016-12-31.csv'

    temp_res, mod, sat = unwrap_path(path)

    # 0.04 for monthly, 0.08 for seasonal
    thresh = 0.08
    binary_psds = psds2binary(path, thresh)
    merged_data = align_with_mirad(binary_psds)

    out_dir = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/conf-matrix-final/movav-classification/amsr2'
    for region, bbox in bboxes.iteritems():
        print region, bbox
        cnfm_over_time_movav(merged_data, bbox, show=False,
                             region="{} {}".format(region,str(bbox)))
        fname = "{}_{}_{}_{}".format(temp_res, mod,sat,region)
        plt.savefig(os.path.join(out_dir, fname + '.pdf'),
                    dpi=300,
                    bbox_inches='tight',
                    format='pdf')
    """
