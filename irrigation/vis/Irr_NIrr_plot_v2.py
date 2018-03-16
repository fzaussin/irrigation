from prep import timeseries
from irrigation.trans import transform
from irrigation.comp import slopes

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import matplotlib
#matplotlib.style.use(['seaborn'])

import pandas as pd

irrigated = 744712
non_irrigated = 750470

window = 35
start = '2016-01-01'
end = '2016-12-31'

"""
ASCAT
"""
ts_I = timeseries.prepare(irrigated,
                 start,
                 end,
                 models=['merra'],
                 satellites=['smapv4',
                             'ascatrecklessrom',
                             'amsr2'
                             ],
                 kind='movav',
                 window=window)

ts_NI = timeseries.prepare(non_irrigated,
                 start,
                 end,
                 models=['merra'],
                 satellites=['smapv4',
                             'ascatrecklessrom',
                             'amsr2'
                             ],
                 kind='movav',
                 window=window)

# rename
ts_I.rename(columns={'merra': 'MERRA-2',
                     'ascatrecklessrom': 'ASCAT',
                     'amsr2': 'AMSR2',
                     'smapv4': 'SMAP'},
            inplace=True)
ts_NI.rename(columns={'merra': 'MERRA-2',
                     'ascatrecklessrom': 'ASCAT',
                     'amsr2': 'AMSR2',
                     'smapv4': 'SMAP'},
             inplace=True)

# calc irrigation
slopes_I = slopes.diffquot_slope(ts_I)
irrig_I = slopes.new_slope_metric(slopes_I)

slopes_NI = slopes.diffquot_slope(ts_NI)
irrig_NI = slopes.new_slope_metric(slopes_NI)

# create fig
plt.figure(figsize=(12, 7))
ax1 = plt.subplot2grid((2, 5), (0, 0))
ax2 = plt.subplot2grid((2, 5), (0, 1), sharex=ax1, sharey=ax1)
ax3 = plt.subplot2grid((2, 5), (1, 0), sharex=ax1)
ax4 = plt.subplot2grid((2, 5), (1, 1), sharex=ax1, sharey=ax3)


lonI, latI = transform.qdeg2lonlat(irrigated)
lonNI, latNI = transform.qdeg2lonlat(non_irrigated)

title_I = r'Irrigated ({lat}$^\circ$N {lon}$^\circ$E)'.format(lat=str(latI),
                                                            lon=str(lonI))
title_NI = r'Non-irrigated ({lat}$^\circ$N {lon}$^\circ$E)'.format(lat=str(latNI),
                                                            lon=str(lonNI))

ax1.set_title(title_I)
ax2.set_title(title_NI)




# max of both ts for ylim
y_max = pd.concat([ts_I, ts_NI]).max().max()
y_min = pd.concat([ts_I, ts_NI]).min().min()
y_max_irrig = pd.concat([irrig_I, irrig_NI]).max().max()

ts_I.plot(ax=ax1, ylim=(y_min, y_max), color=['#404040', '#fb8072', '#80b1d3', '#fdb462'])
ax1.legend(loc=9, ncol=4, mode="expand", borderaxespad=0.)
ts_NI.plot(ax=ax2, color=['#404040', '#fb8072', '#80b1d3', '#fdb462'])
ax2.legend(loc=9, ncol=4, mode="expand", borderaxespad=0.)

# SMAP
irrig_I['SMAP'].plot.area(ax=ax3, label='I', ylim=(0, y_max_irrig), color='#fdb462', stacked=True)
irrig_NI['SMAP'].plot.area(ax=ax4, label='NI', ylim=(0, y_max_irrig), color='#fdb462', stacked=True)
# AMSR2
irrig_I['AMSR2'].plot.area(ax=ax3, label='I', ylim=(0, y_max_irrig), color='#80b1d3', stacked=True)
irrig_NI['AMSR2'].plot.area(ax=ax4, label='NI', ylim=(0, y_max_irrig), color='#80b1d3', stacked=True)
# ASCAT
irrig_I['ASCAT'].plot.area(ax=ax3, label='I', ylim=(0, y_max_irrig), color='#fb8072', stacked=True)
irrig_NI['ASCAT'].plot.area(ax=ax4, label='NI', ylim=(0, y_max_irrig), color='#fb8072', stacked=True)



ax1.set_ylabel(r"SM ($m^{3}m^{-3}$)")
ax3.set_ylabel(r'$SM^{+}_{Irr}$ ($m^{3}m^{-3}$)')
ax1.get_yaxis().set_label_coords(-0.1, 0.5)
ax3.get_yaxis().set_label_coords(-0.1, 0.5)

"""
# plot accumulated values
plt.figure(figsize=(12, 7))
ax1 = plt.subplot2grid((1, 2), (0, 0))
ax2 = plt.subplot2grid((1, 2), (0, 1), sharex=ax1, sharey=ax1)

irrig_I.resample('Q-NOV').sum().plot.area(title='I', ax=ax1)
irrig_NI.resample('Q-NOV').sum().plot.area(title='NI', ax=ax2)
"""

# summe april-august
season_dict = {1:'OOS',2:'OOS',3 : 'OOS', 4 : 'AMJJA', 5 : 'AMJJA', 6 : 'AMJJA' ,
               7:'AMJJA', 8:'AMJJA', 9:'OOS', 10:'OOS', 11:'OOS', 12:'OOS'}


# Write a function that will be used to group the data
def GroupFunc(x):
    return season_dict[x.month]

# Call the function with the groupby operation.
irrig_I_grouped = irrig_I.groupby([lambda x: x.year, lambda x: season_dict[x.month]]).sum()
irrig_NI_grouped = irrig_NI.groupby([lambda x: x.year, lambda x: season_dict[x.month]]).sum()

ascat_I = irrig_I_grouped['ASCAT'].values[0]
amsr2_I = irrig_I_grouped['AMSR2'].values[0]
smap_I = irrig_I_grouped['SMAP'].values[0]

ascat_NI = irrig_NI_grouped['ASCAT'].values[0]
amsr2_NI = irrig_NI_grouped['AMSR2'].values[0]
smap_NI = irrig_NI_grouped['SMAP'].values[0]

# add to plot as textbox
textstr = (r"ASCAT = {:2.2f}".format(ascat_I) + " $m^{3}m^{-3}$ \n" +
           r"AMSR2 = {:2.2f}".format(amsr2_I) + " $m^{3}m^{-3}$ \n" +
           r"SMAP = {:2.2f}".format(smap_I) + " $m^{3}m^{-3}$")
anchored_text = AnchoredText(textstr, loc=1, frameon=True, prop=dict(size=10))
anchored_text.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
ax3.add_artist(anchored_text)

# add to plot as textbox
textstr = (r"ASCAT = {:2.2f}".format(ascat_NI) + " $m^{3}m^{-3}$ \n" +
           r"AMSR2 = {:2.2f}".format(amsr2_NI) + " $m^{3}m^{-3}$ \n" +
           r"SMAP = {:2.2f}".format(smap_NI) + " $m^{3}m^{-3}$")
anchored_text = AnchoredText(textstr, loc=1, frameon=True, prop=dict(size=10))
anchored_text.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
ax4.add_artist(anchored_text)

# fill between
color= 'grey'
alpha = 0.3
ax1.axvspan('2016-01-01', '2016-03-31', color=color, alpha=alpha)
ax1.axvspan('2016-09-01', '2016-12-31', color='grey', alpha=0.3)

ax2.axvspan('2016-01-01', '2016-03-31', color=color, alpha=alpha)
ax2.axvspan('2016-09-01', '2016-12-31', color='grey', alpha=0.3)

ax3.axvspan('2016-01-01', '2016-03-31', color=color, alpha=alpha)
ax3.axvspan('2016-09-01', '2016-12-31', color='grey', alpha=0.3)

ax4.axvspan('2016-01-01', '2016-03-31', color=color, alpha=alpha)
ax4.axvspan('2016-09-01', '2016-12-31', color='grey', alpha=0.3)


# show plots
plt.tight_layout()
plt.show()
