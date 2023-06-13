# coding=utf-8

"""
"""

import os
from tqdm import tqdm
import numpy as np
import subprocess
import pandas as pd
from saramis.mesh import register as r
import matplotlib.pyplot as plt

plot = False
dataset = "amos"
path_cpd = "path_to/coherent_point_drift_cuda/bin/cpd_cmd"
path_full_data = "path_to_data_location"
csv_file = "/path_to/SARAMIS_amos.csv" # Detailing dataset

### Fixed labelled colon.
path_totalsegmentator = "path_to_total"
path_fixed_base =  os.path.join(path_totalsegmentator,"Totalsegmentator_dataset/s0014/colon/fixed_colons/")
path_fixed_org = os.path.join(path_fixed_base, "interp_curve.txt")

path_fixed_ind = [
                  "indices_cecum.txt",
                  "indices_rectum.txt",
                  "indices_hepatic.txt",
                  "indices_splenic.txt",]
indices = [
           [911, 998],
           [0, 114],
           [322, 462],
           [771, 910],]
for i, path in enumerate(path_fixed_ind):
    path_s = os.path.join(path_fixed_base, path)
    arr = np.array(range(indices[i][0], indices[i][1]+1, 1), dtype=int)
    np.savetxt(path_s, arr)
path_fixed_ind_full = [os.path.join(path_fixed_base, path) for path in path_fixed_ind]

if dataset == "amos":
    path_totalsegmentator = os.path.join(path_full_data, "amos22-organized-all/")
    tag = "Data"
    val = 1
    c = "colon_meshes"
    subf = "Orig/colon"
    data = pd.read_csv(csv_file)
    folders_remesh = data[data[c] == val][tag].tolist()
    folders_remesh = ["_".join(["amos", f.split("amos")[1]]) for f in folders_remesh]
elif dataset == "totalsegmentator":
    path_totalsegmentator = os.path.join(path_full_data, "Totalsegmentator_dataset/")
    path_folders = "/media/nina/Expansion/interp_colons_total_seg_fixed.txt"
    with open(path_folders, 'r') as f:
        verify_folders = f.readlines()
        verify_folders = [line.split("\n")[0] for line in verify_folders]
    folders_remesh = verify_folders
    subf = "colon/fixed_colons"
elif dataset == "abdomen1k":
    path_totalsegmentator = os.path.join(path_full_data,"/Abdomen-1k/")
    tag = "Data"
    val = 1
    c = "colon"
    subf = "colon"
    data = pd.read_csv(csv_file)
    folders_remesh = data[data[c] == val][tag].tolist()



for folder in tqdm(folders_remesh):
    path_folder = os.path.join(path_totalsegmentator, folder, subf)
    path_moving = os.path.join(path_folder, "interp_curve.txt")
    path_moving_indices_save = [os.path.join(path_folder, path) for path in path_fixed_ind]
    try:
        # run the CPD CUDA command
        points_f = np.loadtxt(path_fixed_org, delimiter=',')
        points_m = np.loadtxt(path_moving, delimiter=',')
        subprocess.run([path_cpd, path_fixed_org,
                                    path_moving,
                                    path_moving.replace(".txt", "_transformed.txt"),
                                    "--beta", str(float(1.0)),
                                    "--lambda", str(float(10.0)),
                                    "--w", str(0.1)
                                    ])
        # load the registered points
        points_registered = np.loadtxt(path_moving.replace(".txt", "_transformed.txt"), delimiter=',')
        # Over the list of path_fixed_ind, find new points
        registered_indices = []
        fixed_indices = []
        labels = []
        for i, item in enumerate(path_fixed_ind):
            labels.append(item.split("_")[1].split(".")[0])
            points_fixed_cls = np.loadtxt(os.path.join(path_fixed_base, item)).astype(np.int32)
            fixed_indices.append(points_f[points_fixed_cls])
            ind = r.find_closest_point(points_f, points_moving=points_registered, points_fixed_cls=points_fixed_cls)
            points_moving_cls = points_m[ind]
            registered_indices.append(points_moving_cls)
            np.savetxt(path_moving_indices_save[i].replace("indices", "indices_template"), points_moving_cls)
            np.savetxt(path_moving_indices_save[i].replace("indices", "indices_template_int"), ind)
    except:
        print("Error in folder: ", folder)

    if plot:
        for i in range(6):

            fig = plt.figure(figsize=plt.figaspect(0.5))
            ax1 = fig.add_subplot(121, projection="3d")
            ax2 = fig.add_subplot(122, projection="3d")
             #ax[2*i] and ax[(2*i)+1]
            ax1.scatter(points_f[:, 0], points_f[:, 1], points_f[:, 2], color="red", label="Target", alpha=0.1, s=0.5)
            ax2.scatter(points_m[:, 0], points_m[:, 1], points_m[:, 2], color="blue", label="MOVING", alpha=0.1, s=0.5)
            ax1.scatter(fixed_indices[i][:, 0], fixed_indices[i][:, 1], fixed_indices[i][:, 2], color="black", label="Target", alpha=1, s=10)
            ax2.scatter(registered_indices[i][:, 0], registered_indices[i][:, 1], registered_indices[i][:, 2], color="black", label="REGISTERED", alpha=1, s=10)
            ax2.set_title(labels[i] + " Fixed/Template")
            ax1.set_title(labels[i] + " Moving/Registered")
            plt.savefig(os.path.join(path_folder, "colon_" + labels[i] + ".png"))
            # plt.close()
            plt.show()

    print("Rest")
