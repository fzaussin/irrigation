# Copyright (c) 2015,Vienna University of Technology,
# Department of Geodesy and Geoinformation
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
Interface to read the ESA CCI SM data

@author: alexander_gruber@geo.tuwien.ac.at
'''

import os
import numpy as np
import pandas as pd

import pygeogrids.netcdf as ncgrid
from pygeobase.io_base import GriddedTsBase
from pygenio.time_series import IndexedRaggedTs
import pytesmo.timedate.julian as julian


class CCIDs(GriddedTsBase):
    """
    CCI Dataset class reading genericIO data in the CCI common format

    Data in common input format is
    returned as a pandas.DataFrame for temporal resampling.

    Parameters
    ----------
    path : string
        Path to dataset.
    """

    def __init__(self, path):

        grid_fname = os.path.join(path, "ESA-CCI-SOILMOISTURE-LAND_AND_RAINFOREST_MASK-fv04.2.nc")
        grid = ncgrid.load_grid(grid_fname, subset_flag='land')

        super(CCIDs, self).__init__(path, grid, IndexedRaggedTs, mode='r', fn_format='{:04d}')

    def _read_gp(self, gpi):
        """
        Read data into common format

        Parameters
        ----------
        gpi: int
            grid point index

        Returns
        -------
        ts: pandas.DataFrame
            DataFrame including soil moisture, soil moisture noise, and sensor information
        """

        ts = super(CCIDs, self)._read_gp(gpi)

        if ts is None:
            return None

        ts = ts[ts['sm'] != -999999.]
        ts = ts[ts['flag'] == 0]
        ts = ts[(ts['jd'] >= 2299160) & (ts['jd'] <= 1827933925)]

        if ts.size == 0:
            raise IOError("No data for gpi %i" % gpi)

        ts = pd.DataFrame(ts, index=julian.julian2datetimeindex(ts['jd']))
        ts.replace(-999999.,np.nan,inplace=True)

        return ts[['sm','sm_noise','sensor']]


if __name__=='__main__':
    import matplotlib.pyplot as plt

    # gpi = grid point index and references a specific location
    gpi = 737601

    # path to directory with data
    path = '/home/fzaussin/shares/exchange/students/ag/data/ESA_CCI_SM_MERGED_ACT_PASS_v04.1'
    # read data at gpi
    data = CCIDs(path).read(gpi)

    # daily soil moisture estimates
    daily_sm = data['sm']
    # resample to monthly mean soil moisture
    monthly_sm = daily_sm.resample('M').mean()

    # create plot
    daily_sm.plot(label='daily_sm')
    monthly_sm.plot(label='monthly_sm')
    plt.legend()
    plt.show()





