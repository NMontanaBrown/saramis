#coding=utf-8

"""
Script that performs the analysis for the Abdomen-1k + AMOS
data.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import multiprocessing
from saramis.mesh.filtering import get_segment_names_tuples
from saramis.labelling.comparison import compare_preexisting_arr, create_numpy_arrays_before_and_after

new_folder = "/path/to/relabelled/Abdomen-1k"
old_folder = "/path/to/original/Abdomen-1k"
amos = False # If you set to true, will use the amos data
path_to_save_results = "some/path/to/save/results"
filter = 20 # can set this to false so that no filtering is done
segment_names_to_labels, segment_names_tuples = get_segment_names_tuples()

# list folders in old_folder
total_folders = [f for f in os.listdir(old_folder) if "." not in f]
total_folders.sort()


def process_folder(folder):
    if amos:
        base_path_old = os.path.join(old_folder, folder, "Orig")
        base_path_new = os.path.join(new_folder, folder, "Orig")
    else:
        base_path_old = os.path.join(old_folder, folder)
        base_path_new = os.path.join(new_folder, folder)

    path_old = os.path.join(base_path_old,  "auto_seg.seg.nrrd")
    path_new = os.path.join(base_path_new,  "auto_seg.seg.nrrd")
    save_old = os.path.join(base_path_old, "analysis", "auto_seg.npy")
    if filter:
        save_new = os.path.join(base_path_new, "analysis", "auto_seg_filter.npy")
    else:
        save_new = os.path.join(base_path_new, "analysis", "auto_seg_no_filter.npy")

    if not os.path.exists(path_old):
        return folder
    if not os.path.exists(path_new):
        return folder
    else:
        if not os.path.exists(os.path.join(base_path_old, "analysis")):
            os.makedirs(os.path.join(base_path_old, "analysis"))
        if not os.path.exists(os.path.join(base_path_new, "analysis")):
            os.makedirs(os.path.join(base_path_new, "analysis"))

        if os.path.exists(save_new):
            try:
                val = compare_preexisting_arr(save_old, save_new, segment_names_to_labels, path_new)
                file_old = ",".join([folder] + [str(val[2][0, 0]), str(val[2][1, 1]), str(val[2][2, 2])] + [str(item) for item in val[0]])
                file_new = ",".join([folder] + [str(val[2][0, 0]), str(val[2][1, 1]), str(val[2][2, 2])] + [str(item) for item in val[1]])
                return folder, file_old, file_new
            except:
                return folder
        else:
            try:
                val = create_numpy_arrays_before_and_after(path_old,
                                                            path_new,
                                                            save_old,
                                                            save_new,
                                                            segment_names_tuples,
                                                            segment_names_to_labels,
                                                            filter_value=20)
                file_old = ",".join([folder] + [str(val[2][0, 0]), str(val[2][1, 1]), str(val[2][2, 2])] + [str(item) for item in val[0]])
                file_new = ",".join([folder] + [str(val[2][0, 0]), str(val[2][1, 1]), str(val[2][2, 2])] + [str(item) for item in val[1]])
                return folder, file_old, file_new
            except:
                return folder

# MiSSING 11
for i in range(0, total_folders//50):
    error_folders = []
    pixel_old = []
    pixel_new = []
    valid_folders=[]
    pixel_size = []
    # Create a multiprocessing pool with the desired number of processes
    pool = multiprocessing.Pool(processes=20)  # You can adjust the number of processes as per your requirement

    # Map the function to process_folder to the list of total_folders
    if (i+1)*50 > len(total_folders):
        flds = total_folders[i*50:]
    else:
        flds = total_folders[i*50:(i+1)*50]
    for result in tqdm.tqdm(pool.imap_unordered(process_folder, flds), total=len(flds)):
        if len(result) == 1 or result is None or isinstance(result,str):
            error_folders.append(result)
        else:
            valid_folders.append(result[0])
            pixel_old.append(result[1])
            pixel_new.append(result[2])

    # # Close the pool to prevent any more tasks from being submitted to it
    pool.close()

    # # Wait for all the worker processes to finish
    pool.join()
    start = i
    end = (i+1)*50
    if amos:
        fol = "amos"
    else:
        fol = "abdomen1k"

    if filter:
        filter_str = "filter"
    else:
        filter_str = "no_filter"

    with open(os.path.join(path_to_save_results, "pixel_old_{}_{}_{}.txt".format(fol, start, end)), "w") as f:
        header = ["Data", "Pixel_X", "Pixel_Y", "Pixel_Z"] + segment_names_to_labels
        f.write(",".join(header) + "\n")
        for line in pixel_old:
            f.write(line + "\n")

    with open(os.path.join(path_to_save_results, "pixel_new_{}_{}_{}_{}.txt".format(fol, start, end, filter_str)), "w") as f:
        header = ["Data", "Pixel_X", "Pixel_Y", "Pixel_Z"] + segment_names_to_labels
        f.write(",".join(header) + "\n")
        for line in pixel_new:
            f.write(line + "\n")
