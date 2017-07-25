from pygeogrids.grids import genreg_grid
from smap_io.interface import SMAPTs
import time, datetime


tic = time.time()

grid = genreg_grid(grd_spc_lat=0.25, grd_spc_lon=0.25).to_cell_grid()
smap = SMAPTs(ts_path='/home/fzaussin/smap-L3_P_v3')
smap.read_bulk = True


"""
V1
"""
cells = grid.get_cells()
for cell in cells[:10]:
    (gpis, lons, lats) = grid.grid_points_for_cell(cell)
    for i, gpi in enumerate(gpis):
        ts = smap.read(lons[i], lats[i])
toc = time.time()
print "Iterating over cells and then gpis: ", str(datetime.timedelta(seconds=toc - tic))

"""
V1 with iter_gp

tic = time.clock()
cells = grid.get_cells()
for cell in cells[:100]:
    (gpis, lons, lats) = grid.grid_points_for_cell(cell)
    for i, gpi in enumerate(gpis):
        ts = smap.read(lons[i], lats[i])
toc = time.clock()
print "Iterating over cells and then gpis: ", str(datetime.timedelta(seconds=toc - tic))
"""

"""
V2

tic = time.clock()
(gpis, lons, lats, cells) = grid.get_grid_points()
for i, gpi in enumerate(gpis):
    ts = smap.read(lons[i], lats[i])
toc = time.clock()
print "Iterating only over gpis: ", str(datetime.timedelta(seconds=toc - tic))
"""

