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
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    #This function prints and plots the confusion matrix.
    #Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('MIrAD-US')
    plt.xlabel('PSDS')


def prepare_psds_map(path, threshhold=10):
    """
    Create binary psds map based on threshold. For validation with mirad-us.
    :param path:
    :param threshhold:
    :return:
    """
    psds = pd.DataFrame.from_csv(path)
    print psds.head()
    # set threshold to >= 10
    psds[psds < threshhold] = 0.0
    psds[psds >= threshhold] = 1.0
    psds['gpi_quarter'] = psds.index.values
    binary_psds = psds.dropna()
    return binary_psds

def align_with_mirad(binary_psds, threshhold=10):
    """
    Align psds data to mirad data to create one df holding psds over time and
    the irrig_fraction, because confusion_matrix needs input of same length.
    :param psds_data:
    :return:
    """
    mirad = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/validation/mirad_downscaling/mirad-qdeg-binary.csv')
    merged_data = pd.merge(binary_psds, mirad, how='left',
                           on='gpi_quarter')
    merged_data.dropna(axis=0, inplace=True)
    merged_data.drop(['gpi_quarter'], axis=1, inplace=True)
    return merged_data



def iter_conf_matrix(merged_data):
    """
    Iterate over aggregated psds and create conf matrix with mirad-us.
    :param merged_data:
    :return:
    """
    mirad = merged_data['irrig_fraction'].values
    psds_agg = merged_data.drop('irrig_fraction', axis=1)

    for time_agg in psds_agg:
        print time_agg
        cnf_matrix = confusion_matrix(mirad, psds_agg[time_agg].values)
        plt.figure()
        plot_confusion_matrix(cnf_matrix,
                              classes=['irrigated', 'non-irrigated'],
                              normalize=True,
                              title='Normalized confusion matrix for {}'.format(time_agg))

    plt.show()



################################################################################
"""
# import some data to play with
iris = datasets.load_iris()
X = iris.data
y = iris.target
class_names = iris.target_names
print class_names

# Split the data into a training set and a test set
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# Run classifier, using a model that is too regularized (C too low) to see
# the impact on the results
classifier = svm.SVC(kernel='linear', C=0.01)
y_pred = classifier.fit(X_train, y_train).predict(X_test)


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):

    #This function prints and plots the confusion matrix.
    #Normalization can be applied by setting `normalize=True`.

    np.set_printoptions(precision=2)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

# Compute confusion matrix
cnf_matrix = confusion_matrix(y_test, y_pred)
print y_test, y_pred
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names,
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()
"""

if __name__== '__main__':
    np.set_printoptions(precision=2)

    path_div = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/comparison-mult-nomult-crop-fraction/divide-by-cropfraction/divide-by-cropfraction_merra_ascat_reckless_rom_2013-01-01_2013-12-31.csv'
    path_nodiv = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/comparison-mult-nomult-crop-fraction/no-cropfraction/no-cropfraction_merra_ascat_reckless_rom_2013-01-01_2013-12-31.csv'

    binary_psds = prepare_psds_map(path_nodiv, 10)
    merged_data = align_with_mirad(binary_psds)
    iter_conf_matrix(merged_data)
