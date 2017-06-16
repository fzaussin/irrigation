# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:06:27 2016

@author: fzaussin
"""

import os

import pandas as pd
import numpy as np

from _projects.Irrigation_Analysis.temporal_slopes.vis import spatial_plot as mp
from _projects.Irrigation_Analysis.temporal_slopes.trans.path_manipulation import get_file_paths, get_file_name, create_folder, check_fn_length


def change_cbar(in_path_list, out_path, folder_name, cbranges=(0,60)):
    """ Create maps out of .csv file list with specified cbar"""
    
    # create output folder
    res_folder = create_folder(out_path, folder_name)
    
    # iterate trough list of .csv paths and create maps
    for file_path in in_path_list:
        data = pd.DataFrame.from_csv(file_path)
        #TODO: clean up
        file_name = get_file_name(file_path)
        map_title = '{} ('.format(file_name)
        
        mp.spatial_plot_quarter_grid(data, 
                                     title=map_title,
                                     tag_title=True,
                                     tight=True,
                                     region='USA',
                                     cblabel="Positive slope difference sum",
                                     cbrange=cbranges,
                                     path=res_folder,
                                     fname='{}_'.format(file_name))
                                     
    message = 'Maps successfully created'
    print message
    
    
def create_difference_maps(path_list,
                           out_path,
                           folder_name,
                           reference_fn='ascat_2007.csv',
                           cbranges=None):
    """
    Create year-wise difference maps.
    """
    # create output folder
    res_folder = create_folder(out_path, folder_name) 
    
    # load reference data
    reference_file_path = [s for s in path_list if reference_fn in s][0]
    reference_data = pd.DataFrame.from_csv(reference_file_path)
    ref_year = check_fn_length(reference_fn)
    
    # iterate trough list of .csv paths and create difference maps
    for file_path in path_list:
        yearly_data = pd.DataFrame.from_csv(file_path)
        # calc difference
        reference_data.ix[:,1:] = (yearly_data.ix[:,1:]
                                 - reference_data.ix[:,1:])
        difference_data = reference_data
        
        # get current year for fn and map title
        curr_year = check_fn_length(get_file_name(file_path))   
        out_file_name = 'diff_{}_{}.csv'.format(curr_year,
                                                ref_year)
                                              
        # save to csv
        # TODO: integrate mask_gpis
        difference_data.to_csv(os.path.join(res_folder, out_file_name))
        print out_file_name  
        
        # create maps
        # TODO: integrate vis.maps.map_maker
        file_name = get_file_name(file_path)
        #TODO: change map title for differences !!!
        map_title = '{} ('.format(file_name)
        
        mp.spatial_plot_quarter_grid(difference_data, 
                                     title=map_title,
                                     tag_title=True,
                                     tight=True,
                                     region='USA',
                                     cblabel="Positive slope difference sum",
                                     cbrange=cbranges,
                                     path=res_folder,
                                     fname='diff_{}_{}_'.format(file_name, ref_year))
                                     
    print 'Maps successfully created'


if __name__ == "__main__":
    # Create Difference Maps Vol. 2 (22.03.2017)

    # collect files
    search_path = r"D:\_data\_Results\Slope_Analysis\v4_2016-12-19"
    path_list = get_file_paths(search_path,
                               '.csv',
                               'ascat')
    print path_list
    print len(path_list)

    # create maps
    # reference = 2007 -> Differences
    out_path = r"X:\students\fzaussin\E2O\Results\ASCAT_ERA"
    folder_name = "Differences"
    create_difference_maps(path_list, out_path, folder_name, 'ascat_2007.csv')

    # reference = Climatology 2007-2013 -> Anomalies
    out_path = r"X:\students\fzaussin\E2O\Results\ASCAT_ERA"
    folder_name = "Anomalies"
    create_difference_maps(path_list, out_path, folder_name, 'ascat_2007-2013.csv')

    """"""

    #%% Create difference maps
    #%%
    # ASCAT

    """
    search_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19"
    path_list = get_file_paths(search_path,
                               '.csv',
                               'ascat')

    # reference = 2007
    out_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19\Difference_Maps\ASCAT"
    folder_name = "Reference_2007"
    create_difference_maps(path_list, out_path, folder_name, 'ascat_2007.csv')

    # reference = 2013
    out_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19\Difference_Maps\ASCAT"
    folder_name = "Reference_2013"
    create_difference_maps(path_list, out_path, folder_name, 'ascat_2013.csv')

    # reference = Climatology 2007-2013
    out_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19\Difference_Maps\ASCAT"
    folder_name = "Reference_Climatology"
    create_difference_maps(path_list, out_path, folder_name, 'ascat_2007-2013.csv')

    #%%
    # AMSRE

    search_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19"
    path_list = get_file_paths(search_path,
                               '.csv',
                               'amsre')

    ## reference = 2002
    #out_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19\Difference_Maps\AMSRE"
    #folder_name = "Reference_2002"
    #create_difference_maps(path_list, out_path, folder_name, 'amsre_2002.csv')

    # reference = 2011
    out_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19\Difference_Maps\AMSRE"
    folder_name = "Reference_2011"
    create_difference_maps(path_list, out_path, folder_name, 'amsre_2011.csv')

    # reference = Climatology 2002-2011
    out_path = r"D:\_data\Results\Slope_Analysis\v4_2016-12-19\Difference_Maps\AMSRE"
    folder_name = "Reference_Climatology"
    create_difference_maps(path_list, out_path, folder_name, 'amsre_2002-2011.csv')
    """















