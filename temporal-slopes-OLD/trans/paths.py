# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 13:30:48 2016

@author: fzaussin

PATH SPECIFICATIONS AND FUNCTIONS
"""

import os

import numpy as np
import pandas as pd

def create_folder(dir_path, folder_name):
    """
    """
    res_path = os.path.join(dir_path, folder_name)
    
    if not os.path.exists(res_path):
        os.makedirs(res_path)
        return res_path
    else:
        error_message = 'Path already exists: {}'.format(res_path)
        return error_message
        
def get_file_paths(root_path, file_ext, search_word=None):
    """
    """
    file_list = []
    
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(file_ext):
                 file_list.append(os.path.join(root, file))             
    if search_word is not None:
        file_list = [fpath for fpath in file_list if search_word in fpath]
        
    return file_list
    
    
def get_file_name(root_path):
    """
    """
    fn_ext = os.path.basename(root_path)
    fn = fn_ext.split('.')[0]
    return fn

def check_fn_length(file_name):
    """
    """
    # check for climatology (year-year)
    if len(file_name) > 14:
        year = file_name[6:15]
    else:
        year = file_name[6:10]
    return year
    
#    if len(ref_fn) > 14 and len(curr_fn) > 14:
#        ref_year = ref_fn[6:15]
#        curr_year = curr_fn[6:15]
#    elif len(ref_fn) > 14 and len(curr_fn) <= 14:
#        ref_year = ref_fn[6:15]
#        curr_year = curr_fn[6:10]
#    elif len(ref_fn) < 14 and len(curr_fn) > 14:
#        ref_year = ref_fn[6:10]
#        curr_year = curr_fn[6:15]
#    else:
#        ref_year = ref_fn[6:10]
#        curr_year = curr_fn[6:10] 
#
#    return ref_year, curr_year
    

def sort_file_paths(file_list):
    """
    """
    #df = pd.DataFrame(columns=['ascat','amsre','amsr2'])
    
    ascat, amsre, amsr2 = [],[],[]
    for file, counter in enumerate(file_list):
        fn, fe = os.path.splitext(os.path.basename(file))
        if fn[:5] == 'ascat':
            ascat.append(file_list[counter])
        elif fn[:5] == 'amsre':
            amsre.append(file_list[counter])
        elif fn[:5] == 'amsr2':
            amsr2.append(file_list[counter])
    print ascat, amsre, amsr2
    return ascat, amsre, amsr2