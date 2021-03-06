# -*- coding: utf-8 -*-
"""
Created on Tue Aug 02 15:59:06 2016

@author: fzaussin

Plotting routines for quarter degree data
"""

import os
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


# use seaborn style
import seaborn as sns
sns.set_style("white")
sns.set(rc={'axes.facecolor':'#ffffff', 'figure.facecolor':'#ffffff'})


def spatial_plot_quarter_grid(data, tags=None, region='USA', title='',
                              tag_title=False, cbar=True, cblabel='',
                              cbrange=None, cmap='BuGn', labelpad=-75,
                              fontsize=20, figsize=(20, 10), tight=True,
                              path=None, fname='',
                              type=None):
    """"""

    # generate 0.25° meshgrid
    lons = (np.arange(360 * 4) * 0.25) - 179.875
    lats = (np.arange(180 * 4) * 0.25) - 89.875
    lons, lats = np.meshgrid(lons, lats)

    # set tags to df cols
    if tags is None:
        tags = data.columns

    # iterate over cols/vars in df and create map
    for tag in tags:
        print tag
        # initialize empty img
        img = np.empty(lons.size, dtype='float32')
        img.fill(None)

        # fill img with data
        img[data['gpi_quarter'].values] = data[tag]

        # mask array where invalid values (nans) occur
        img_masked = np.ma.masked_invalid(img.reshape((180 * 4, 360 * 4)))

        # create figure
        fig = plt.figure(num=None, figsize=figsize, dpi=90, facecolor='w', edgecolor='k')

        if region == 'USA':
            # USA
            m = Basemap(width=5000000, height=3000000,
                        projection='laea',
                        lat_ts=50, lat_0=38.7, lon_0=-97.5,
                        resolution='c')
            # set properties
            m.drawcoastlines(color='#191919', zorder=2)
            m.drawcountries(color='#333333', zorder=2)
            m.drawstates(color='#666666', zorder=2)
            #m.fillcontinents(color='#f2f2f2', zorder=0)
            m.fillcontinents(color='#d9d9d9', zorder=0)
        elif region == 'egypt':
            m = Basemap(llcrnrlon=27.,
                        llcrnrlat=26,
                        urcrnrlon=35.,
                        urcrnrlat=32.5)
            # set properties
            m.drawcoastlines()
            m.drawcountries()
            m.drawstates()
        else:
            # global
            m = Basemap()
            m.drawcoastlines()
            m.drawcountries()

        # give nan values special color
        #cmap = plt.get_cmap(cmap)
        #cmap.set_bad(color='w', alpha=1.)
        """
        # temporarily plot markers
        markersize = 12
        # cali irrig
        lon, lat = -121.87 + 0.125, 39.38 + 0.125
        x, y = m(lon, lat)
        m.plot(x, y, 'ro', markersize=markersize)

        # cali non-irrig
        lon, lat = -122.375 + 0.125, 40.375 + 0.125
        x, y = m(lon, lat)
        m.plot(x, y, 'r^', markersize=markersize)

        # idaho irrig
        lon, lat = -114.625 + 0.125, 42.625 + 0.125
        x, y = m(lon, lat)
        m.plot(x, y, 'ro', markersize=markersize)

        # idaho non-irrig
        lon, lat = -115.375 + 0.125, 42.625 + 0.125
        x, y = m(lon, lat)
        m.plot(x, y, 'r^', markersize=markersize)

        # mississ irrig
        lon, lat = -90.125 + 0.125, 35.625 + 0.125
        x, y = m(lon, lat)
        m.plot(x, y, 'ro', markersize=markersize)

        # mississ non-irrig
        lon, lat = -89.375 + 0.125, 35.375 + 0.125
        x, y = m(lon, lat)
        m.plot(x, y, 'r^', markersize=markersize)
        """
        # create img
        im = m.pcolormesh(lons, lats, img_masked, cmap=cmap, latlon=True, zorder=1)

        # auto scaling
        if cbrange is not None:
            im.set_clim(vmin=cbrange[0], vmax=cbrange[1])

        # colorbar
        """ old:
        cbar = fig.colorbar(im, ticks=[0, 10, 20, 30, 40, 50])
        cbar.ax.set_yticklabels(['0', '10', '20', '30', '40', '> 50'])  # vertically oriented colorbar
        """
        if cbar:
            cbar = plt.colorbar(im, pad=0.01)#, extend='max')

            # cbar label
            if cblabel is None:
                cbar.set_label(tag, fontsize=fontsize)
            else:
                cbar.set_label(cblabel, labelpad=20, y=0.5, fontsize=fontsize)

            # ticks
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(fontsize)

        # title
        if title == 'tag' and type is None:
            tmp_title = tag
        elif title == 'tag' and type == 'seasonal':
            year = tag[:4]
            month = tag[5:7]

            month2season = {'05': 'MAM',
                            '08': 'JJA',
                            '11': 'SON',
                            '02': 'DJF',
                            # for gpi_quarter
                            'ua': 'grid points'}
            season = month2season.get(month)
            tmp_title = year + ' ' + season

        else:
            tmp_title = title
        plt.title(tmp_title, fontsize=fontsize)

        # layout
        if tight is True:
            plt.tight_layout()

        # figure export
        if path is None:
            plt.show()
        else:
            if not os.path.exists(path):
                os.makedirs(path)
            #TODO: changed from \\ to / for linux...
            #fpath = path + '/' + fname + str(tag) + '.png'
            fpath = os.path.join(path, fname + '_' + str(tag) + '.png')
            plt.savefig(fpath,
                        format='png',
                        dpi=fig.dpi,
                        bbox_inches='tight',
                        facecolor=fig.get_facecolor())


def spatial_plot(data, lons, lats, cbrange=(0,100)):
    """

    :param data:
    :return:
    """
    # create figure
    fig = plt.figure(num=None, figsize=(20,10), dpi=90, facecolor='w', edgecolor='k')

    # create basemap
    m = Basemap(width=5000000, height=3000000,
                projection='laea',
                lat_ts=50, lat_0=38.7, lon_0=-97.5,
                resolution='c')
    # set properties
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()

    # create img
    im = m.pcolormesh(lons, lats, data, cmap='coolwarm', latlon=True)
    cbar = plt.colorbar(im, pad=0.01)
    im.set_clim(vmin=cbrange[0], vmax=cbrange[1])

    plt.tight_layout()
    plt.show()


def map_maker(csv_data, map_title='', path_results=None, fname=''):
    """
    Wrapper around spatial_plot_quarter_grid for Irrigation_Analysis plots

    :param csv_data:
    :param map_title:
    :param path_results:
    :return:
    """

    # single months
    spatial_plot_quarter_grid(data=csv_data,
                              cmap='Blues',
                              tags=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                              title=map_title,
                              path=path_results,
                              fname=fname,
                              # default args
                              tag_title=True,
                              tight=True,
                              region='USA',
                              cblabel=r'$SM^{+}_{Irr}$ ($m^{3}m^{-3}$)',
                              cbrange=(0, 0.05))

    # climatologies
    spatial_plot_quarter_grid(data=csv_data,
                              cmap='Blues',
                                 tags=['MAM', 'JJA', 'SON'],
                                 title=map_title,
                                 path=path_results,
                                 fname=fname,
                                 # default args
                                 tag_title=True,
                                 tight=True,
                                 region='USA',
                                 cblabel=r'$SM^{+}_{Irr}$ ($m^{3}m^{-3}$)',
                                 cbrange=(0, 0.15))

    # AMJJASO (April - October)
    spatial_plot_quarter_grid(data=csv_data,
                              cmap='Blues',
                                 tags=['AMJJASO'],
                                 title=map_title,
                                 path=path_results,
                                 fname=fname,
                                 # default args
                                 tag_title=True,
                                 tight=True,
                                 region='USA',
                                 cblabel=r'$SM^{+}_{Irr}$ ($m^{3}m^{-3}$)',
                                 cbrange=(0, 0.20))
    pass


def lcmask_map(csv_data, map_title=None, path_results=None, fname=None):
    """
    Wrapper around spatial_plot_quarter_grid for Irrigation_Analysis plots
    :param csv_data:
    :param map_title:
    :param path_results:
    :return:
    """

    # single months
    spatial_plot_quarter_grid(data=csv_data,
                              tags=['crop_mask'],
                              title=map_title,
                              path=path_results,
                              fname=fname,
                              # default args
                              tag_title=True,
                              tight=True,
                              region='global',
                              cblabel='Fraction of rainfed crop area [%]',
                              cbrange=(0, 1))
    pass



if __name__ == '__main__':
    import pandas as pd

    path = '/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/FIXED/NEW-METRIC/USA/climats/smapv4-merra-climat-based.csv'
    data = pd.DataFrame.from_csv(path)
    data['gpi_quarter'] = data.index.values

    # drop empty columns
    data = data.dropna(axis=1, how='all')

    """
    map_maker(data,
              path_results='/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/climatology-based/amsr2/new_cbar'
              )
    

    dir = os.path.split(path)[0]
    fname = os.path.split(path)[1]
    region, mod, sat = fname.split('_')[:3]
    print region, mod, sat
    #outpath = '/home/fzaussin'
    """

    spatial_plot_quarter_grid(data,
                              title='tag',
                              tight=True,
                              region='USA',
                              cbrange=(0,0.05),
                              cmap='Blues',
                              cblabel=r'$SM^{+}_{Irr}$ ($m^{3}m^{-3}$)',
                              #type='seasonal'
                              path='/home/fzaussin/shares/users/Irrigation/Data/output/new-results/PAPER/FINAL/FIXED/NEW-METRIC/USA/climats/smapv4')
                              #fname='{}_{}'.format(mod, sat))# + '_v4')
