import numpy as np
import pandas as pd

from datetime import timedelta

def slopes_climat(df):
    """operates only on climat and without data gaps!"""
    # calculate slope using 1st and 3rd, then 2nd and 4th value
    window = [-1, 0, 1]
    x = np.arange(1, 367)

    df_slopes = pd.DataFrame(index=df.index)
    for series in df.columns:
        slopes_y = np.convolve(df[series], window, mode='same')
        slopes_x = np.convolve(x, window, mode='same')
        df_slopes[series] = np.divide(slopes_y,
                                      slopes_x) # all x negative
    return df_slopes

def psd(df, start, end):
    """"""
    df = df[start:end]
    reference_index = 0
    model = df[df.columns.values[reference_index]]
    df = df.drop([df.columns.values[reference_index]], axis=1)
    # new_df = pd.DataFrame
    for series in df:
        # satellite - model slope element wise
        slope_diffs = np.subtract(df[series].values, model.values)
        pos_slope_diffs = slope_diffs[slope_diffs > 0]
        psd_sum = pos_slope_diffs.sum()
        print series
        print "Days where sat>mod: ", len(pos_slope_diffs)
        print "PSDS: ", psd_sum
        print ""
    """
        df[series] = pd.Series(
            slope_diffs,
            index=df.index)
    return df
    """
    pass


if __name__=='__main__':
    import matplotlib.pyplot as plt
    from irrigation.prep import ts

    # 721798 is mississippi example gpi
    df = ts.prepare(gpi=726120,
            start_date='2007-01-01',
            end_date='2013-12-31',
            kind='clim')
    df.plot()

    # slopes
    df_slopes = slopes_climat(df)
    #slopes.plot(kind='bar')

    # 'JJA' : (151,243),
    psd(df_slopes, 151, 243)
    plt.show()

