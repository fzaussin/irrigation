"""
create gmia plot for comparison with global results
"""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
# use seaborn style
import seaborn as sns
sns.set_style("white")
sns.set(rc={'axes.facecolor':'#f0f0f0', 'figure.facecolor':'#f0f0f0'})

import numpy as np


data = np.loadtxt('/home/fzaussin/shares/users/Irrigation/validation/gmia/gmia_v5_aei_pct.asc', skiprows=6)
data = data[::-1]

x = (np.arange(4320)*0.083333333333333) - 180
y = (np.arange(2160)*0.083333333333333) - 90

fig = plt.figure(num=None, figsize=(20,10), dpi=90, facecolor='w', edgecolor='k')

m = Basemap()
m.drawcoastlines()
m.drawcountries()

img = m.pcolormesh(x,y,data, cmap='BuGn')

cbar = plt.colorbar(img, fraction=0.046, pad=0.04)
cbar.set_label('Fraction of AEI [%]', labelpad=20, y=0.5, fontsize=20)

plt.title('Area equipped for irrigation (AEI)', fontsize=20)
plt.show()