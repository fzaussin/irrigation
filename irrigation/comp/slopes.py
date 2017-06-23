import numpy as np
import pandas as pd

from datetime import timedelta

def calc_slopes(df):
    """"""
    window = [-1, 0, 1]

    df_slopes = pd.DataFrame(index=df.index)
    for series in df.columns:
        df_slopes[series] = np.divide(np.convolve(df[series], window, mode='same'),
                                      #np.convolve(np.arange(len(df.index.values)), window, mode='same'))
                                      (len(window) - 1))
    return df_slopes


if __name__=='__main__':
    import matplotlib.pyplot as plt
    from irrigation.prep import ts

    df = ts.prepare(gpi=721798,
            start_date='2007-01-01',
            end_date='2013-12-31',
            kind='movav')
    print df
    df.plot()
    slopes = calc_slopes(df)
    print slopes
    slopes.plot()

    plt.show()
