# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

import types

import scipy.fftpack as fft
from scipy.optimize import fminbound
from scipy.ndimage import distance_transform_edt


def InitialGuess(y):
    if len(np.where(np.isnan(y))[0]) == 0:
        z = y
    else:
        vint = np.vectorize(int)
        I = vint(np.isnan(y))
        L = distance_transform_edt(I, return_indices=True, return_distances=False)
        z = y
        z[np.where(I)] = y[L[0][np.where(I)]]

    zshp = z.shape
    z = fft.dct(z, norm='ortho')
    for k in np.arange(len(zshp)):
        z[np.int(np.ceil(zshp[k] / 10.))::] = 0
        if len(zshp) > 1:
            z = np.rollaxis(z, 1)
    z = fft.idct(z, norm='ortho')

    return z

def smoothn(y_in, s=None, w=0, robust=False, MaxIter=100, TolZ=1e-3, z0=None, W=None, weightstr='bisquare'):
    """
    MOVED FROM MATHNEW/SMOOTHN
    :param y_in:
    :param s:
    :param w:
    :param robust:
    :param MaxIter:
    :param TolZ:
    :param z0:
    :param W:
    :param weightstr:
    :return:
    """
    y = y_in.copy()

    if y.size < 2:
        z = y
        return z

    shp = np.array(y.shape)

    # normalize weights if provided
    if type(W) == types.NoneType:
        W = np.ones(shp)
    W[np.isnan(y)] = 0
    W /= max(W)
    is_weighted = len(np.where(W < 1)[0]) > 0

    #    shp = (5,3,2)

    # Lambda Tensor (Eigenvalues of difference matrix)
    d = len(shp)
    Lambda = np.zeros(shp)

    for i in np.arange(d):
        tmp_shp = np.ones(d)
        tmp_shp[i] = shp[i]
        Lambda += np.cos(np.pi * (np.arange(1, np.int(shp[i]) + 1).reshape(np.int(tmp_shp)) - 1) / np.int(shp[i]))

    Lambda = -2 * (d - Lambda)

    if type(s) != types.NoneType:
        Gamma = 1. / (1 + s * Lambda ** 2)

    # Bounds for smoothness parameter
    N = len(np.where(shp != 1)[0])
    hMin = 1e-6
    hMax = 0.99
    sMinBnd = (((1 + np.sqrt(1 + 8 * hMax ** (2 / N))) / 4 / hMax ** (2 / N)) ** 2 - 1) / 16
    sMaxBnd = (((1 + np.sqrt(1 + 8 * hMin ** (2 / N))) / 4 / hMin ** (2 / N)) ** 2 - 1) / 16

    # Set initial conditions
    w_total = W

    if is_weighted == True:
        if type(z0) != types.NoneType:
            z = z0
        else:
            z = InitialGuess(y)
    else:
        z = np.zeros(shp)

    z0 = z
    y[np.isnan(y)] = 0

    tol = 1
    RobItProc = True
    RobStep = 1
    n_it = 0
    err_p = 0.1
    RF = 1.75 if is_weighted else 1.0

    # Main iteration process
    while RobItProc:

        # amount of weights
        aow = w_total.sum() / W.size  # 0 < aow <= 1

        while (tol > TolZ) & (n_it < MaxIter):

            n_it += 1
            y_dct = fft.dct(w_total * (y - z) + z, norm='ortho')

            # Use generalized cross-validation method to generate s
            if (type(s) == types.NoneType) & (np.log2(n_it) % 1 == 0):
                s = fminbound(gcv, np.log10(sMinBnd), np.log10(sMaxBnd), xtol=err_p)

            z = RF * fft.idct(Gamma * y_dct, norm='ortho') + (1 - RF) * z

            tol = np.linalg.norm(z0 - z) / np.linalg.norm(z) if is_weighted else 0
            z0 = z

        if robust == True:
            h = np.sqrt(1 + 16 * s)
            h = np.sqrt(1 + h) / np.sqrt(2) / h
            h = h ** N;

            w_total = W * RobustWeights(y - z, h, weightstr);

            is_weighted = True
            tol = 1
            n_it = 0;

            RobStep += 1;
            RobItProc = RobStep < 4
        else:
            RobItProc = False

    if s > 0:
        if np.abs(np.log10(s / sMinBnd)) < err_p:
            print 'Warning... lower bound for s has been reached!'
            raise
        if np.abs(np.log10(s / sMaxBnd)) < err_p:
            print 'Warning... upper bound for s has been reached!'
            raise
    if n_it >= MaxIter:
        print 'Warning... Maximum number of iteration has been reached!'
        raise

    return z


def check_continuity(tmp_ts,max_gap=5):
    
    ts = tmp_ts.copy()    
    
    istart = []
    iend = []
    lens = []
    oklens = []

    in_seg = False
    nan_cnt = 0
  
    for ind in ts.index:
        
        if not np.isnan(ts[ind]):
            nan_cnt = 0
            not_nan = ind 
            if in_seg == False:
                istart.append(np.where(ts.index==ind)[0][0].astype('int'))
                in_seg = True
                
        else:
            nan_cnt += 1
            if (in_seg==True)&(nan_cnt==max_gap):
                iend.append(np.where(ts.index==not_nan)[0][0].astype('int'))
                in_seg = False

    if len(iend) < len(istart):
        iend.append(len(ts)-1)
    
    for ind in np.arange(len(istart)):
        
        seg = ts.iloc[istart[ind]:iend[ind]+1]
        lens.append(len(seg))
        oklens.append(len(seg[~np.isnan(seg)]))
        
    return istart, iend, lens, oklens

def add_nan(dataframe):
    idx = pd.date_range(dataframe.index[0], dataframe.index[-1])
    dataframe.index = pd.DatetimeIndex(dataframe.index)
    dataframe = dataframe.reindex(idx, fill_value=np.nan) #float('NaN')
    return dataframe  
    
def fill_gaps(tmp_data,max_gap=10):

    data = tmp_data.copy()
    
    istart, iend, lens, oklens = check_continuity(data,max_gap=max_gap)

    for ind in np.arange(len(istart)):
        smoothed = smoothn(data.iloc[istart[ind]:iend[ind]+1].values.copy(),s=0)
        # DF_Time['sm_nogaps'] = smoothed
        data.iloc[istart[ind]:iend[ind]+1] = smoothed
        data[data<0]=0
        
    return data

def iter_fill(df, max_gap=10):
    """"""
    df_gapfill = pd.DataFrame(index=df.index)
    for col in df.columns:
        df_gapfill[col] = fill_gaps(df[col], max_gap)
    return df_gapfill


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # w/o gapfill
    ts = pd.DataFrame.from_csv("/home/fzaussin/Desktop/fill-gaps-test")
    ts.plot()
    plt.show()

    # with gapfill
    ts_gapfill = iter_fill(ts)
    ts_gapfill.plot()
    plt.show()