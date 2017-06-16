# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 09:34:20 2015

@author: agruber
"""


import pywt

import numpy as np
import pandas as pd

from USER_DEV.ag.unimelb.smoothn import smoothn
#from math.smoothn import smoothn

def convert_dyadic_length(tmp_data):
    
    data = tmp_data.copy()
    
    N = (data.index[-1]-data.index[0]).days+1
    J = np.ceil(np.log2(N))
    
    dyadic_dates = pd.date_range(start=data.index[0],periods=2**J)
    data = data.combine_first(pd.DataFrame({},index=dyadic_dates))
    
    return data
    
    
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
    
    
def fill_gaps(tmp_data,max_gap=5):
    
    data = tmp_data.copy()
    
    istart, iend, lens, oklens = check_continuity(data,max_gap=max_gap)

    for ind in np.arange(len(istart)):
        
        smoothed = smoothn(data.iloc[istart[ind]:iend[ind]+1].values.copy(),s=0)
        data.iloc[istart[ind]:iend[ind]+1] = smoothed
        data[data<0]=0
        
    return data
            
    
def wavelet_decomp_single_ts(tmp_data,j_steps=6,base='db4'):
    
    data = tmp_data.copy()
    
    N = len(data)
    j_max = np.log2(N)
    
    if j_max < j_steps:
        print 'Not enough data to decompose into %i steps!' % j_steps
        return None
    
    if j_max%1 != 0:
        print 'Input data must be of dyadic length!'
        return None

    mask = np.isnan(data).values
    if len(np.where(mask)[0]) > 0.8 * N:
        print 'Too little valid data'
        return None
    
    # fill NaN values
    smoothed_data = smoothn(data.values.copy(),s=0)
    
    # calculate wavelet coefficients
    cDA = pywt.wavedec(smoothed_data,base,mode='per',level=j_steps)
         
    # reconstruct wavelets
    DA = pd.DataFrame({'a%0i'%(j_steps): pywt.upcoef('a',cDA[0],base,level=j_steps,take=N)})
    for j in np.arange(1,j_steps+1):
        DA['d%0i' % j] = pywt.upcoef('d',cDA[len(cDA)-j],base,level=j,take=N)

    # mask NaN values
    DA.loc[mask]=np.nan

    return DA
    

def wavelet_decomp(tmp_data,j_steps=6):

    data = tmp_data.copy()

    # fill temporal gaps and extend to dyadic length
    data = convert_dyadic_length(data)
    
    # fill NaN values 
    for ds in data:
        data[ds] = fill_gaps(data[ds])
    
    # perform wavelet analysis
    result = {}
    for ds in data:
        result[ds] = wavelet_decomp_single_ts(data[ds],j_steps=j_steps)
        
    return result
    
    
def read_test_data():
    
    data_path = r'H:\Documents\MATLAB\user_dev\multiscale' + '\\'
    
    ascat = pd.Series.from_csv(data_path + 'ascat.csv',sep=';',header=0)
    amsre = pd.Series.from_csv(data_path + 'amsre.csv',sep=';',header=0)
    merra = pd.Series.from_csv(data_path + 'merra.csv',sep=';',header=0)
    
    mint = max([min(ascat.index),min(amsre.index),min(merra.index)])
    maxt = min([max(ascat.index),max(amsre.index),max(merra.index)])
    
    data = pd.DataFrame({},index=np.arange(mint,maxt+1).astype('int'))
    data['ascat']=ascat
    data['amsre']=amsre
    data['merra']=merra.groupby(level=0).first()

    data.index = pd.date_range(start='2001-01-01',periods=len(data))
    
    return data

        
if __name__=='__main__':
#    
    data = read_test_data()
    result = wavelet_decomp(data)


#    pass











    