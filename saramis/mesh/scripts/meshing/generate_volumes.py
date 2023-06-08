# coding = utf-8

"""
Script to get tetrahedral volumes for simulation
using tetwild or ftetwild
"""

import os
import subprocess
import multiprocessing
import tqdm


path_base="path/to/dataset"
path_ftetwild = "path/to/fTetWild/build/FloatTetwild_bin"
DOCKER_IMAGE="yixinhu/tetwild" # If using docker, remember to run newgrp docker before this script.
dataset = "total_segmentator" # "amos", "total_segmentator", "abdomen_1k"

total_folders = os.listdir(path_base)

if dataset == "amos":
    total_folders = [folder for folder in total_folders if "amos" in folder]
elif dataset == "total_segmentator":
    total_folders = [folder for folder in total_folders if folder[0] == "s"]
elif dataset == "abdomen_1k":
    total_folders = [folder for folder in total_folders if "case_" in folder]

total_folders.sort()
for folder in tqdm.tqdm(total_folders):
    base_folder = os.path.join(path_base, folder)
    if dataset == "amos":
        base_folder = os.path.join(base_folder, "Orig")

    path_meshes = os.path.join(base_folder, "full_meshes")

    if not os.path.exists(path_meshes):
        continue

    meshes = os.listdir(path_meshes)

    def process_mesh(mesh):
        path_ply = os.path.join(path_meshes, mesh, mesh+"_laplace_smooth_mesh_decimation_centered_global.ply")
        if not os.path.exists(path_ply):
            return None
        if os.path.exists(path_ply.replace(".ply", "_.msh")):
            return None
        wd = os.getcwd()
        os.chdir(os.path.join(path_meshes, mesh))
        docker_command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{subprocess.run(['pwd'], capture_output=True, text=True).stdout.strip()}:/data",
            "yixinhu/tetwild",
            "./"+mesh+"_laplace_smooth_mesh_decimation.ply",
            "-q"]
        subprocess.run(docker_command)
        os.chdir(wd)
        subprocess.run(["gmsh", path_ply.replace(".ply", "_.msh"), "-1", "-0", path_ply.replace(".ply", ".vtk"), "-2"])

    def process_mesh_ftetwild(mesh):
        path_ply = os.path.join(path_meshes, mesh, mesh+"_laplace_smooth_mesh_decimation_centered_global.ply")
        if not os.path.exists(path_ply):
            return None
        # if os.path.exists(path_ply.replace(".ply", "_.msh")):
        #     return None
        subprocess.run([path_ftetwild, "-i", path_ply, "--is-quiet"])
        subprocess.run(["gmsh", path_ply.replace(".ply", "_.msh"), "-1", "-0", path_ply.replace(".ply", ".vtk"), "-2"])

    pool = multiprocessing.Pool(processes=8)
    for _ in tqdm.tqdm(pool.imap(process_mesh_ftetwild, meshes), total=len(meshes)):
        pass
    pool.close()
    pool.join()
