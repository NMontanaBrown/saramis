# coding=utf-8

"""
Script that hollows out specific meshes
in the dataset.
"""

import os
import multiprocessing
from saramis.mesh.mesh_finetuning import hollow_mesh
from saramis.mesh.filtering import get_hollow_segments

path_base="path/to/dataset"
path_ftetwild = "path/to/fTetWild/build/FloatTetwild_bin"
dataset = "total_segmentator" # "amos", "total_segmentator", "abdomen_1k"

folders_to_hollow = get_hollow_segments()

total_folders = os.listdir(path_base)

if dataset == "amos":
    total_folders = [folder for folder in total_folders if "amos" in folder]
elif dataset == "total_segmentator":
    total_folders = [folder for folder in total_folders if folder[0] == "s"]
elif dataset == "abdomen_1k":
    total_folders = [folder for folder in total_folders if "case_" in folder]

total_folders.sort()
for folder in total_folders:
    path_base_f = os.path.join( path_base, folder, "full_meshes")
    if dataset == "amos":
        path_base_f = os.path.join(path_base_f, "Orig", "full_meshes")
    meshes = os.listdir(path_base_f)
    meshes_to_hollow = [f for f in meshes if f in folders_to_hollow]
    meshes_to_hollow.sort()
    
    def process_mesh(mesh):
        path_mesh = os.path.join(path_base_f, mesh, mesh+"_laplace_smooth_mesh_decimation_centered_global.ply")
        hollow_mesh(path_mesh)
    
    pool = multiprocessing.Pool(processes=8)
    for _ in pool.imap_unordered(process_mesh, meshes_to_hollow):
        pass
    pool.close()
    pool.join()

    