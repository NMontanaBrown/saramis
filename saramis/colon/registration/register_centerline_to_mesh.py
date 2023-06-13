# coding=utf-8

"""
Registers the centerline to it's own space mesh.
We also get the points of the mesh closest to the
labelled centerline.
"""

import os
from tqdm import tqdm
import numpy as np
import subprocess
import pandas as pd
from saramis.mesh import register as r
import matplotlib.pyplot as plt

path_cpd = "/path_to/coherent_point_drift_cuda/bin/cpd_cmd" # Path to cpd executable
                                                            # Follow repo instructions to install.
csv_file = "/path_to/SARAMIS_amos.csv" # Detailing dataset
path_base = "/path_to_dataset/amos22-organized-all/"
dataset = "amos"
plot = False # whether or not to produce plots.

if dataset == "amos":
    tag = "Data"
    val = 1
    c = "colon_meshes"
    subf = "Orig/colon" # structure for folder, "Orig/colon" for amos, "colon" for abdomen-1k
    curve = "jitter" # Which blender mode used to extract data.
    data = pd.read_csv(csv_file)
    folders_remesh = data[data[c] == val][tag].tolist()
elif dataset == "abdomen1k":
    tag = "Data"
    val = 1
    c = "colon"
    subf = "colon"
    curve = "sin_jitter"
    data = pd.read_csv(csv_file)
elif dataset == "totalsegmentator":
    data = pd.read_csv(csv_file)
    c = "colon"
    val = 1
    tag = "image_id"
    subf = "colon"
    curve = "jitter"

folders_remesh = data[data[c] == val][tag].tolist()

if dataset == "amos":
    folders_remesh = ["_".join(["amos", f.split("amos")[1]]) for f in folders_remesh]


for folder in tqdm(folders_remesh):
    path_fixed_org = os.path.join(path_base,folder,subf, curve,"interp_curve.ply")
    subprocess.run(["meshio", "ascii", path_fixed_org])

    # Indices in the centerline which correspond to each segment
    path_moving_ind = [
                        "indices_template_int_cecum.txt",
                        "indices_template_int_rectum.txt",
                        "indices_template_int_hepatic.txt",
                        "indices_template_int_splenic.txt",]
    path_fixed_ind = [item.replace("template", "final_mesh") for item in path_moving_ind]
    path_fixed_ind_full = [os.path.join(path_base, folder, subf, path) for path in path_fixed_ind]
    path_folder = os.path.join(path_base, folder, subf)
    path_moving = os.path.join(path_folder, "interp_curve.txt")
    path_moving_indices = [os.path.join(path_folder, path) for path in path_moving_ind]
    try:
        points_f = r.load_points(path_fixed_org)
        np.savetxt(path_fixed_org.replace(".ply", "_register_mesh.txt"), points_f, delimiter=',')
        points_m = np.loadtxt(path_moving, delimiter=',')
        # We get the aligned centerline
        subprocess.run([path_cpd, path_fixed_org.replace(".ply", "_register_mesh.txt"),
                                    path_moving,
                                    path_moving.replace(".txt", "_transformed_centerline_final_space.txt"),
                                    "--beta", str(float(1.0)),
                                    "--lambda", str(float(10.0)),
                                    "--w", str(0.1)
                                    ])
        # load the registered points
        points_registered = np.loadtxt(path_moving.replace(".txt", "_transformed_centerline_final_space.txt"), delimiter=',')
        # Over the list of path_fixed_ind, find new points in the rendering mesh corresponding to those points.
        registered_indices = []
        fixed_indices = []
        labels = []

        for i, item in enumerate(path_moving_ind):
            labels.append(item.split("_")[1].split(".")[0])
            points_moving_cls = np.loadtxt(os.path.join(path_folder, item)).astype(np.int32)
            registered_indices.append(points_registered[points_moving_cls])
            ind = r.find_closest_point_radius(points_registered, points_moving=points_f, points_fixed_cls=points_moving_cls, r=20)
            points_f_cls = points_f[[int(i) for i in ind]]
            fixed_indices.append(points_f_cls)
            np.savetxt(path_fixed_ind_full[i].replace("_int", ""), points_f_cls)
            np.savetxt(path_fixed_ind_full[i], ind)

        if plot:
            for i in range(6):
                fig = plt.figure(figsize=plt.figaspect(0.5))
                ax1 = fig.add_subplot(121, projection="3d")
                ax2 = fig.add_subplot(122, projection="3d")
                #ax[2*i] and ax[(2*i)+1]
                ax1.scatter(points_f[:, 0], points_f[:, 1], points_f[:, 2], color="red", label="Target", alpha=0.1, s=0.5)
                ax2.scatter(points_registered[:, 0], points_registered[:, 1], points_registered[:, 2], color="blue", label="MOVING", alpha=0.1, s=0.5)
                ax1.scatter(fixed_indices[i][:, 0], fixed_indices[i][:, 1], fixed_indices[i][:, 2], color="black", label="Target", alpha=1, s=10)
                ax2.scatter(registered_indices[i][:, 0], registered_indices[i][:, 1], registered_indices[i][:, 2], color="black", label="REGISTERED", alpha=1, s=10)
                ax2.set_title(labels[i] + " Fixed/Template")
                ax1.set_title(labels[i] + " Moving/Registered")
                plt.savefig(os.path.join(path_folder, "colon_" + labels[i] + ".png"))
                plt.show()
    except:
        print("Error in folder: ", folder)
