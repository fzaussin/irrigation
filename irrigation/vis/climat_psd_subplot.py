# -*- coding: utf-8 -*-

from irrigation.prep import timeseries, interp
from irrigation.trans import transform
from irrigation.comp import slopes

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

gpi = 789361
location = ''

climat = timeseries.prepare(gpi=gpi,
                        start_date='2007-01-01',
                        end_date='2016-12-31',
                        models=['merra'],
                        satellites=['ascatrecklessrom'],
                        kind='clim')
# calc psd
slopes_climat = slopes.diffquot_slope_climat(climat)
pos_slope_diffs = slopes.psd(slopes_climat)

plt.figure(figsize=(15, 10))
ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)

lon, lat = transform.qdeg2lonlat(gpi)
title = r'{loc} {lat}$^\circ$N {lon}$^\circ$E'.format(loc=location,
                                                      lat=str(lat),
                                                      lon=str(lon))

# first row
climat.plot(ax=ax1, title=title)
ax1.legend(loc=3)
ax1.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
# second row
pos_slope_diffs.plot(ax=ax2, kind='bar')
ax2.set_ylabel(r"Positive slope difference ($d^{-1}$)")
ax2.set_xlabel("DOY")

# adjust x ticks
N_x = 30
ticks = ax2.xaxis.get_ticklocs()
ticklabels = [l.get_text() for l in ax2.xaxis.get_ticklabels()]
ax2.xaxis.set_ticks(ticks[::N_x])
ax2.xaxis.set_ticklabels(ticklabels[::N_x])

# plot
plt.tight_layout()
plt.show()