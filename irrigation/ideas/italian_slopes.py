from irrigation.inout import importdata
from irrigation.comp import slopes
from pytesmo import scaling

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

gpi = 726000
data = importdata.QDEGdata()
ts = data.read_gpi(gpi, '2007-01-01', '2016-12-31',
                        model='merra',
                        satellites=['ascat_reckless_rom',
                                    #'amsr2',
                                    #'smap'
                                    ])
# drop nans and scale
ts = ts.dropna()
ts_scaled = scaling.scale(ts, 'mean_std', 0)

ax = ts_scaled.plot(title=str(gpi))#, ylim=(0,1))
ax.set_ylabel(r"Soil moisture ($m^{3}/m^{3}$)")
ax.set_xlabel('Datetime')

# count irrig events
df_slopes = slopes.local_slope(ts_scaled)
irrig_counts = slopes.slope_metric_italians(df_slopes)

# plot
irrig_counts.plot(title='Counts where dsm_sat > dsm_mod (Gpi = {})'.format(gpi))
plt.show()