# coding=utf-8

"""
Script that performs matching of segments
produced from manual VMTK processing.
"""

import os
import numpy as np
import os
import json
import csv
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d, splev
from scipy.interpolate import splprep, BSpline
import pandas as pd
from saramis.colon.utils import (parse_directory,
                                 read_csv,
                                 read_mrk_json,
                                 find_next_segment)


plot = False # Set to True to plot the results
path_to_dataset_csvs = "path_to_csvs"
path_to_data_folder = "path_to_data_folder"
dataset = "abdomen_1k"
path_save_output_interp = "path_to_save_output_interp"
if dataset == "abdomen_1k":
    csv_file = os.path.join(path_to_dataset_csvs, "SARAMIS_Abdomen1k.csv")
    path_totalsegmentator = os.path.join(path_to_data_folder,
                                         "Abdomen-1k")
    data = pd.read_csv(csv_file)
    folders_remesh = data[data["colon"] == 1]["Data"].tolist()
    folders_remesh.sort()
elif dataset == "amos":
    csv_file =  os.path.join(path_to_dataset_csvs, "SARAMIS_amos.csv")
    path_totalsegmentator = os.path.join(path_to_data_folder, "amos22-organized-all/")
    data = pd.read_csv(csv_file)
    folders_remesh = data[data["colon_meshes"] == 1.0]
    folders_remesh = ["amos_"+case.split("amos")[1] for case in folders_remesh["Data"].tolist()]
elif dataset == "totalsegmentator":
    csv_file =  os.path.join(path_to_dataset_csvs,"SARAMIS_TotalSegmentator.csv")
    path_totalsegmentator = os.path.join(path_to_data_folder,"Totalsegmentator_dataset")
    data = pd.read_csv(csv_file)
    folders_remesh = data[data["colon"] == 1.0]["image_id"].tolist()

verify_folders = []
for folder_m in folders_remesh:
    path = os.path.join(path_totalsegmentator, folder_m, "colon")
    folders = os.listdir(path)
    jsons = [folder for folder in folders if folder.endswith(".json")]
    jsons_start = [folder for folder in jsons if "start" in folder]
    if jsons_start:
        verify_folders.append(folder_m)

single_centerlines = [] # some folders did not need to be multiply matched.
for folder in folders_remesh:
    path_folder = os.path.join(path_totalsegmentator, folder, "colon")
    folders = os.listdir(path_folder)
    jsons = [folder for folder in folders if folder.endswith(".json")]
    if len(jsons) ==1:
        single_centerlines.append(folder)
print(len(single_centerlines))


for folder in verify_folders:
    path = os.path.join(path_totalsegmentator, folder, "colon")
    if dataset == "amos":
        path = os.path.join(path_totalsegmentator,folder, "Orig", "colon")
    arrays = parse_directory(path)
    point_start = os.path.join(path, "start.mrk.json")

    if os.path.splitext(point_start)[1]==".fcsv":
        point_start = read_csv(point_start)
        start_point = np.array(point_start[1:]).astype(np.float64)
    elif os.path.splitext(point_start)[1]==".json":
        point_start = read_mrk_json(point_start)
        start_point = np.array(point_start).astype(np.float64)

    data_format = find_next_segment(start_point, arrays)
    # Smooth the data - filter out values with large jumps between
    # consecutive points
    x = data_format[:, 0]
    y = data_format[:, 1]
    z = data_format[:, 2]

    jump = np.sqrt(np.diff(x)**2 + np.diff(y)**2 + np.diff(z)**2) 
    smooth_jump = gaussian_filter1d(jump, 5, mode='wrap')  # window of size 5 is arbitrary
    limit = 2*np.median(smooth_jump)    # factor 2 is arbitrary
    xn, yn, zn = x[:-1], y[:-1], z[:-1]
    xn = xn[(jump > 0) & (smooth_jump < limit)]
    yn = yn[(jump > 0) & (smooth_jump < limit)]
    zn = zn[(jump > 0) & (smooth_jump < limit)]
    # Interpolate
    tck, u = splprep([xn, yn, zn])
    unew = np.arange(0, 1, 0.001) # 1000 points.
    out = splev(unew, tck)
    
    ##### Plot
    if plot:
        data_format = np.concatenate([arrays[0][::-1], arrays[1]])
        fig = plt.subplot(111, projection='3d')
        fig.scatter(data_format[:, 0], data_format[:, 1], data_format[:, 2], alpha=0.1)
        fig.plot(out[0], out[1], out[2], 'r')
        plt.show()
    arr_interp = np.array(out).T

    # Save, for blender
    np.savetxt(os.path.join(path, "interp_curve.txt"), arr_interp, delimiter=",")

set_multiple = set(verify_folders)
set_single = set(single_centerlines)

new_singles_no_problems = []
for folder in single_centerlines:
    path = os.path.join(path_totalsegmentator, folder, "colon")
    if dataset == "amos":
        path = os.path.join(path_totalsegmentator,folder, "Orig", "colon")
    arrays = parse_directory(path)
    arr = np.array(arrays[0])
    if arr.shape[0] ==2:
        print(folder)
        continue
    new_singles_no_problems.append(folder)
    x = arr[:, 0]
    y = arr[:, 1]
    z = arr[:, 2]
    fig = plt.subplot(111, projection='3d')
    tck, u = splprep([x, y, z])
    unew = np.arange(0, 1, 0.001)
    out = splev(unew, tck)
    fig.plot(out[0], out[1], out[2], 'r')
    arr_interp = np.array(out).T
    np.savetxt(os.path.join(path, "interp_curve.txt"), arr_interp, delimiter=",")

set_no_probs = set(new_singles_no_problems)
set_all = list(set_multiple.union(set_no_probs))
with open(os.path.join(path_save_output_interp, "interp_colons_{}.txt".format(dataset)), 'w') as outfile:
    for fname in verify_folders:
        outfile.write(fname+"\n")