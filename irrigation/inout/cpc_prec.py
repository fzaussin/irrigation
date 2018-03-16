import xarray as xr
from trans.transform import qdeg2lonlat

cpc_data = xr.open_dataset('/home/fzaussin/data/CPC/precip.V1.0.2012-2016.nc')

def read_cpc(gpi_qdeg):
    """"""
    lon, lat = qdeg2lonlat(gpi_qdeg)
    # degrees east
    prec_ts = cpc_data.precip.sel(lon=360+lon, lat=lat)
    prec_ts_df = prec_ts.to_dataframe()
    return prec_ts_df['precip']

if __name__=='__main__':
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style('ticks')

    prec = read_cpc(728880)
    prec.plot()

    plt.show()