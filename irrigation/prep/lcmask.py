#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Created on 03-03-2017 

@author: fzaussin
@email: felix.zaussinger@geo.tuwien.ac.at

Temporal solution for applying a land-cover mask to the Irrigation_Analysis data (.csv's)
    - the mask shows rainfed cropland at a 0.25° resolution from 0 to 100%
    - applied to the "old" .csv files

"""
#TODO: solve conflict with lcmask (!)
#TODO: re-write and integrate in process


import numpy as np
import pandas as pd

import netCDF4 as nc


def load_lcmask(param='fLC.10'):
    """
    Load a land cover mask at 0.25 resolution for a single parameter, which defaults to rainfed cropland

    :return: list of gpis
    """
    import netCDF4 as nc
    lc_mask = nc.Dataset(
        '/home/fzaussin/shares/radar/Datapool_processed/ESA_CCI_LC/datasets/img_0d25_annual_v1-4/ESACCI-LC-L4-LCCS-Map-300m-P5Y-2010-v1.4_combined100-0d25-fLC.nc'
    )

    # extract data to 1d array, reverse order, convert to df
    masked_gpis = lc_mask.variables[param][:, ::-1, :]
    masked_gpis_1d = np.ma.getdata(masked_gpis).flatten()
    df_masked_gpis = pd.DataFrame(masked_gpis_1d)

    # add index column and rename
    df_masked_gpis.reset_index(level=0, inplace=True)
    df_masked_gpis.rename(columns={0: 'crop_mask', 'index': 'gpi_quarter'}, inplace=True)

    return df_masked_gpis


def mask_gpis(irrig_fpath, treshhold=0.05):
    """
    Extract gpis from input Irrigation_Analysis data .csv's which correspond with the lc-mask

    :param irrig_fpath:
    :return: list of masked gpis
    """
    irrig_data = pd.DataFrame.from_csv(irrig_fpath)
    print irrig_data
    masked_gpis = load_lcmask()

    # merge data frames: colname = gpi_quarter
    merged_data = pd.merge(irrig_data, masked_gpis, how='left', on='gpi_quarter')
    # drop masked out gpis
    masked_data = merged_data.loc[(merged_data['crop_mask'] >= treshhold) & (merged_data['crop_mask'] <= 1.0)]
    return masked_data

def merge_lcmask_params(param1, param2):
    """"""
    gpis1 = load_lcmask(param1)
    gpis2 = load_lcmask(param2)
    # merge data frames: colname = gpi_quarter
    merged_data = pd.merge(gpis1, gpis2, how='left', on='gpi_quarter')
    return merged_data

def lcmask_tresh(treshhold=0.05):
    """"""
    # TODO: temporal only for plot
    lcmask = load_lcmask()
    masked_data = lcmask.loc[(lcmask['crop_mask'] >= treshhold) & (lcmask['crop_mask'] <= 1.0)]
    return masked_data


if __name__ == '__main__':
    from irrigation.vis import spatialplot


    path = '/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/QDEG_pointlist_USA.csv'
    masked_gpis = mask_gpis(path)
    print masked_gpis
    masked_gpis.to_csv('/home/fzaussin/shares/users/Irrigation/Data/lookup-tables/LCMASK_rainfed_cropland_usa.csv')

    """
    df = merge_lcmask_params('fLC.10', 'fLC.20')
    treshhold = 0.05
    masked_data = df.loc[(df['crop_mask_x'] > treshhold) | (df['crop_mask_y'] > treshhold)]
    print masked_data
    """


    """
    Plot ASCAT-ERA maps the nice way

    # get df fpaths
    path_list = pm.get_file_paths(root_path='/home/fzaussin/shares/users/Earth2Observe/Irrigation/Data/AMSR2',
                                  file_ext='.csv',
                                  search_word='amsr2')
    # create plots
    outpath = '/home/fzaussin/shares/users/Earth2Observe/Irrigation/Plots/AMSR2-ERA'

    for fpath in path_list:
        # apply lcmask to data (only plot areas outlined as rainfed crops) > 0.05% of Area
        masked_data = mask_gpis(fpath, treshhold=0.05)
        # create spatial plots for each df
        spatial_plot.map_maker(csv_data=masked_data,
                               map_title='',
                               path_results=outpath,
                               fname=pm.get_file_name(fpath))
    """

    """
    Plot LC-MASK
    """

    """
    spatial_plot.lcmask_map(csv_data=data_temp,
                            map_title='',
                            path_results=out,
                            fname='lc_mask_100%')

    """
