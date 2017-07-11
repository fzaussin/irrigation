# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 17:04:15 2016

@author: fzaussin

FFT Irrigation
"""

import numpy as np
import pandas as pd
from scipy import signal

#from pytesmo import scaling
from irrigation.inout import importdata
from irrigation.prep import interp

import matplotlib.pyplot as plt




def prepare_ts(gpi, start_date, end_date):
    """"""
    # read ts
    data_object = importdata.QDEGdata()
    ts = data_object.read_gpi_old(gpi, start_date, end_date, 'ascat')
    # gapfill
    ts_gapfill = interp.iter_fill(ts, 5)
    ts_gapfill = ts_gapfill.dropna()
    # scaling
    #ts_scaled = scaling.scale(ts_gapfill, 'mean_std', 0)
    return ts_gapfill

def plot_spectrum(gpi):
    """
    Plots a Single-Sided Amplitude Spectrum of ts(t)
    """
    # read ts, fill gaps
    ts = prepare_ts(gpi, start_date='2007-01-01', end_date='2011-12-31')
    
    # detrend
    ts_detrend = ts - ts.mean()
    
    # construct sample frequencies
    n = len(ts_detrend) # length of the signal
    
    # define cycles per unit: days = 1, week=7, month=31, years = 365.25
    days = 365.25
    time_step = 1.0 / days
    frq = np.fft.fftfreq(n, d = time_step)
    frq = frq[range(n/2)] # one side frequency range
    
    # fft computing and normalization
    TS = np.fft.fft(ts_detrend)/n 
    TS = TS[range(n/2)]
    
    # plot    
    f, ax = plt.subplots(3,figsize=(10,10))
    
    f.suptitle("Single Sided Amplitude Spectrum of ASCAT-Ts at Gpi: %d" % gpi,
                 fontsize=16)
    ax[0].plot(ts)
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('SM [%]')
    ax[0].set_yticks(np.arange(0,120,20))
    
    ax[1].plot(frq,abs(TS),'r') # plotting the spectrum
    ax[1].set_xlabel('Frequency (cycles per %d days)' % days)
    ax[1].set_ylabel('|TS(freq)|')
    ax[1].set_xlim(0,182.5)
    ax[1].set_ylim(0,6)
    ax[1].set_xticks(np.arange(0,200,25))
    ax[1].set_yticks(np.arange(0,8,1))
    
    ax[2].plot(frq,abs(TS),'r') # plotting the spectrum
    ax[2].set_xlabel('Frequency (cycles per %d days)' % days)
    ax[2].set_ylabel('|TS(freq)|')
    ax[2].set_xlim(0,13)
    ax[2].set_xticks(range(13))
    ax[2].set_yticks(np.arange(0,13,2))
    
    f.tight_layout()
    f.subplots_adjust(top=0.92)
    plt.show()
    

if __name__=='__main__':
    plot_spectrum(720358)
    



    
    
    
    

    
