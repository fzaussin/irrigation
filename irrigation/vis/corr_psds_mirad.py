import pandas as pd


psds_monthly = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/climatology-based/ascat-merra-climat-based-months.csv')
mirad = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/validation/mirad_downscaling/mirad-25km/mirad25kmv2_lat_lon_gpi_025degrees.csv')

merged_data = pd.merge(psds_monthly, mirad, how='left',
                           on='gpi_quarter')


