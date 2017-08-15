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

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


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


def iter_conf_matrix(merged_data, show=False):
    """
    Iterate over aggregated psds and create conf matrix with mirad-us.
    :param merged_data:
    :return:
    """
    mirad = merged_data['irrigation'].values
    print mirad
    psds_agg = merged_data.drop('irrigation', axis=1)

    cnf_matrix_dict = {}

    for time_agg in psds_agg:
        print time_agg
        cnf_matrix = confusion_matrix(mirad, psds_agg[time_agg].values)

        # normalize and append to dict
        cm_norm = cnf_matrix.astype('float') / cnf_matrix.sum(axis=1)[:, np.newaxis]
        cm_norm = np.round(cm_norm, 2)
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

def cnfm_over_time(data, bbox=None, region=''):
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

    # create barplot with custom colors
    title = region

    ax = cnfm_over_time.plot.bar(
        color=['#018571', '#dfc27d', '#80cdc1', '#a6611a'],
        title=title, stacked=True, ylim=(0, 200), alpha=0.7)
    ax.set_ylabel('Percent (%)')
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.show()



if __name__== '__main__':
    #np.set_printoptions(precision=2)
    from irrigation.vis.spatialplot import spatial_plot_quarter_grid
    import matplotlib
    matplotlib.style.use(['ggplot', 'seaborn-poster'])

    ###
    # subsets
    bbox_cali = (-124.48, 32.53, -114.13, 42.01) # state
    bbox_nebraska = (-104.0535,40.0,-95.3081,43.0013) # state
    bbox_georgia = (-85.6051,30.3558,-80.7514,35.0008) # state

    bbox_mississ_flood_plain = (-92.3621,31.2175,-88.9893,37.6186) # ausschnitt
    bbox_snake_river_valley = (-117.243,41.9881,-111.0436,44.4534) # ausschnitt

    # for tests only
    bbox_northdakota = (-104.05,45.94,-96.55,49.0)
    bbox_texas = (-106.65,25.84,-93.51,36.5)
    bbox_arizona = (-114.8184,31.3322,-109.0452,37.0043)
    ###
    # make psds and mirad binary based on thresh
    monthly_psds = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/climatology-based/ascat-merra-climat-based-months.csv'

    thresh = 0.04
    binary_psds = psds2binary(monthly_psds, thresh)
    merged_data = align_with_mirad(binary_psds)

    # plot binary maps
    #spatial_plot_quarter_grid(merged_data, title='tag', cbrange=(0,1), cblabel='Binary irrigated area')

    # create conf-matrix bar plot
    cnfm_over_time(merged_data, bbox=bbox_snake_river_valley, region='Snake River basin '+ str(bbox_snake_river_valley))


