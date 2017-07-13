from rsdata.TRMM_TMPA.interface import Tmpa3B42Ts

def trmm_reader(lon, lat):
    """read 6 hourly trmm data"""
    trmm = Tmpa3B42Ts()
    trmm_data = trmm.read_ts(lon, lat)
    return trmm_data['pcp']
