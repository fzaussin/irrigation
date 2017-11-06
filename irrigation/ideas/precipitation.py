from rsdata.TRMM_TMPA.interface import Tmpa3B42Ts
from pytesmo.time_series import anomaly
import numpy as np
from trans.transform import qdeg2lonlat


import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates

matplotlib.style.use('ggplot')


def trmm_reader(gpi):
    """read 6 hourly trmm data"""
    trmm = Tmpa3B42Ts()
    lon, lat = qdeg2lonlat(gpi)
    trmm_data = trmm.read_ts(lon, lat)
    # set outliers to nan
    trmm_data.loc[trmm_data['pcp'] == -9999.900391] = np.nan
    return trmm_data['pcp']

if __name__=='__main__':
    gpi = 696364
    prec_ts_natres = trmm_reader(gpi)


    # climatology
    daily_pcp = prec_ts_natres.resample('D').sum()
    daily_pcp.plot()
    """
    daily_climat = anomaly.calc_climatology(daily_pcp)

    daily_climat.plot(title='daily climat')

    # calc anomaly
    climat = anomaly.calc_climatology(prec_ts_natres)
    anom= anomaly.calc_anomaly(prec_ts_natres, climatology=climat)
    monthly_anom = anom.resample('M').sum()

    #ax = monthly_anom.plot(title='TRMM monthly anomaly', ylim = (-20,30))
    #ax.set_ylabel(r"Precipitation ($mm$)")
    """
    #
    plt.show()
