# coding=utf-8

"""
"""

import os
import meshio
import pymeshlab as ml
import subprocess
import saramis.mesh.mesh_finetuning as mf
import multiprocessing
import vtk
import nrrd
import tqdm

path_base = "path/to/Totalsegmentator_dataset/"
path_to_save = "path/to/savetxtfile"
total_folders = os.listdir(path_base)

# pick one here
dataset = "total_segmentator" # "amos", "abdomen1k", "total_segmentator"
if dataset == "total_segmentator":
    total_folders = [folder for folder in total_folders if "s" in folder]
elif dataset == "amos":
    total_folders = [folder for folder in total_folders if "amos_" in folder]
elif dataset == "abdomen1k":
    total_folders = [folder for folder in total_folders if "case_" in folder]

total_folders.sort()
err_folderss=[]

for folder in total_folders:
    path_test_b = os.path.join(path_base, folder, "full_meshes")
    if dataset == "amos":
        path_test_b = os.path.join(path_base, folder, "Orig", "full_meshes")
    if not os.path.exists(path_test_b):
        continue
    folders = os.listdir(path_test_b)

    def process_folder(fo):
        err_folder = None
        path_test = os.path.join(path_test_b, fo, "{}.ply".format(fo))
        if os.path.exists(path_test.replace(".ply", "_laplace_smooth_mesh_decimation.ply")):
            return None
        if not os.path.exists(path_test):
            return fo
                
        files_not_to_delete = [".ply",
                            "_laplace_smooth_mesh_decimation.ply",]
        files_not_to_delete = [fo+i for i in files_not_to_delete]
        # 2. Quadric edge collapse
        mf.laplacian_smooth_mesh(path_test)
        mf.mesh_decimation(path_test.replace(".ply", "_laplace_smooth.ply"))

        full_files = os.listdir(os.path.dirname(path_test))
        for file in full_files:
            if file not in files_not_to_delete:
                os.remove(os.path.join(os.path.dirname(path_test), file))
        return None

    pool = multiprocessing.Pool(processes=10)
    for err_folder in tqdm.tqdm(pool.imap_unordered(process_folder, folders), total=len(folders)):
        if err_folder:
            err_folderss.append(os.path.join(path_test_b, err_folder))
            print(err_folder)
    pool.close()
    pool.join()

with open(os.path.join(path_to_save,"/err_folders_remeshing_ply_{}.txt".format(dataset)), "w") as f:
    for err_folder in err_folderss:
        f.write(err_folder + "\n")
