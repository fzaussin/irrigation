import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

from inout.importdata import QDEGdata
from ideas.precipitation import trmm_reader

gpi = 696364

data = QDEGdata()

ts = data.read_gpi(gpi, '2012-01-01', '2016-12-31',
                   models=[],
                   satellites=['amsr2'])
print ts
ts.plot()
plt.show()