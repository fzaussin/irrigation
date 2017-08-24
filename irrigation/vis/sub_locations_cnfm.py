from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def draw_screen_poly( lats, lons, m):
    x, y = m( lons, lats )
    xy = zip(x,y)
    poly = Polygon( xy, facecolor='red', alpha=0.4 )
    plt.gca().add_patch(poly)

def bbox2latlons(bbox):
    """convert bbox to lat lon arrays"""
    lats = [bbox[1], bbox[3], bbox[3], bbox[1]]
    lons = [bbox[0], bbox[0], bbox[2], bbox[2]]
    return (lats, lons)

bbox = (-124.48, 32.53, -114.13, 42.01)

#lats = [32.53, 42.01, 42.01, 32.53]
#lons = [-124.48, -124.48, -114.13, -114.13]

#lats = [ -30, 30, 30, -30 ]
#lons = [ -50, -50, 50, 50 ]

if __name__=='__main__':

    fig = plt.figure(figsize=(15,8))
    # draw bmap
    m = Basemap(width=5000000, height=3000000,
                            projection='laea',
                            lat_ts=50, lat_0=38.7, lon_0=-97.5,
                            resolution='c')
    # set properties
    m.drawcoastlines(color='#191919', zorder=2)
    m.drawcountries(color='#333333', zorder=2)
    m.drawstates(color='#666666', zorder=2)
    m.fillcontinents(color='#f2f2f2', zorder=0)

    bboxes = {'California': (-124.48, 32.53, -114.13, 42.01),
              'Nebraska': (-104.05, 40.00, -95.31, 43.00),
              'Georgia': (-85.61, 30.36, -80.75, 35.00),
              'Mississippi': (-92.36, 31.21, -88.98, 37.61)}

    for area in bboxes.iteritems():
        region = area[0]
        bbox = area[1]
        # get lat lons from bbox
        lats, lons = bbox2latlons(bbox)
        draw_screen_poly(lats, lons, m)

    plt.title("Locations of the bounding boxes", fontsize=20)
    plt.tight_layout()
    plt.show()