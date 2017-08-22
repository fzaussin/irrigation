# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('ticks')
matplotlib.style.use(['seaborn-poster'])


# MODIS NDVI climatology using 16-day data from 2007-2016
# for 0.25° footprint at 36.875,-89.375 pixel center location
# mean reduce with gee from 250m native resolution
ndvi_irri_monthy = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/mississ-comp-new/modis-16day-ndvi/irrigated_pixel_monthly_mean.csv')
ndvi_irri = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/mississ-comp-new/modis-16day-ndvi/irrigated_pixel.csv')

# determine 50% threshold for SOS and EOS phenology
thresh = ndvi_irri_monthy.max() - ((ndvi_irri_monthy.max() - ndvi_irri_monthy.min()) / 2)
print thresh

ndvi_ratio = (ndvi_irri_monthy-ndvi_irri_monthy.min()) / (ndvi_irri_monthy.max() - ndvi_irri_monthy.min())
print ndvi_ratio


# GPCC full reanalysis precipitation from Datapool,
# climatology calculated using 2007-2013 monthly values
# nearest neighbor to above pixel in 1° (?) grid
gpcc = pd.DataFrame.from_csv('/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/mississ-comp-new/gpcc/ra_2007_2013_climatology.csv')

# concatenate data and insert empty zero, so that the plots has same space at the x axis limits
concat = pd.concat([ndvi_irri_monthy,gpcc], axis=1)
concat.loc[0] = [np.nan, np.nan]
concat = concat.sort_index()


# create plot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.bar(range(1,13), gpcc.prec.values, color='#4292c6', edgecolor='#525252', alpha=0.7)
ax1.set_ylim(0,160)
ax1.set_ylabel('Precipitation (mm/month)')

ax2.plot(range(1,13), ndvi_irri_monthy.NDVI_mean.values, color='#006d2c', marker='o')
ax2.set_ylim(0,0.8)
ax2.set_ylabel('NDVI')

# plot threshhold line
#ax2.plot(range(1,13), np.repeat(0.54, len(range(1,13))), color='black', linestyle=':')

# create grid
ax1.grid(True, color='#d9d9d9')
gridlines = ax1.get_xgridlines() + ax1.get_ygridlines()
for line in gridlines:
    line.set_linestyle(':')


# create title
location = r'36.75$^\circ$N -89.25$^\circ$E'
plt.title('Upper Mississippi Basin ({})'.format(location))

# map # of month to string
plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11,12], ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

plt.tight_layout()
plt.show()