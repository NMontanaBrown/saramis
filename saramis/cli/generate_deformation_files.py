# coding=utf-8

"""
CLI that allows for a given folder containing individual organ meshes to be
processed into simulation files.
"""

import os
import subprocess
import argparse
import meshio
import pymeshlab as pmesh
import saramis.mesh.mesh_finetuning as mf
import shutil


def process_meshes(path_nii2mesh,
                   path_tetgen,
                   path_organ,
                   save_folder_path,
                   final_folder):
    """
    Function that uses usrs local nii2mesh compiled library,
    and compiled tetgen library, with a given organ mesh in .nii.gz format
    and performs a quadric edge collapse,
    followed by a volume generation with tetgen,
    and moves them to a final save location for simulation.
    :param path_nii2mesh: str, path to local install of nii2mesh library
    :param path_tetgen: str, path to local install of tetgen
    :param path_organ: str, path to organ that one wants to set up simulation for.
    :param save_folder_path: str, intermediate save path for all the files required for final simulation.
    :param final_folder: str, final save location for .ply, and .vtu files. .vtu is the tetrahedral
                         volume, .ply is the surface/visual model.
    """
    # 1. Convert to .ply, nii2mesh
    # try:
    organ = path_organ.split("/")[-1] # base file
    subprocess.run([path_nii2mesh, path_organ, os.path.join(save_folder_path, organ.replace(".nii.gz", ".ply"))])
    # except:
    #     print("Error with meshing of nii file.")
    try:
        subprocess.run(["meshio", "ascii", os.path.join(save_folder_path, organ.replace(".nii.gz", ".ply"))])

        # 2. Quadric edge collapse
        mf.laplacian_smooth_mesh(os.path.join(save_folder_path, organ.replace(".nii.gz", ".ply")))
        mf.mesh_decimation(os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth.ply")))

        # 3. Generate volume with tetgen
        subprocess.run(["meshio", "ascii", os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.ply"))])
        try:
            subprocess.run([path_tetgen, "-Ykq", os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.ply"))])
        except:
            print("Error with tetgen")
        subprocess.run(["meshio", "convert", os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.1.vtk")),
                                             os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.vtu"))])
        subprocess.run(["meshio", "ascii", os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.vtu"))])

        paths = [os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.ply")),
                os.path.join(save_folder_path, organ.replace(".nii.gz", "_laplace_smooth_mesh_decimation.vtu"))]
        for path in paths:
            subprocess.run(["mv", path, path.replace(save_folder_path, final_folder)])
    except:
        print("Error with file")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_nii2mesh")
    parser.add_argument("path_tetgen")
    parser.add_argument("path_organ")
    parser.add_argument("save_folder_path")
    parser.add_argument("final_folder")
    args = parser.parse_args()
    process_meshes(args.path_nii2mesh,
                   args.path_tetgen,
                   args.path_organ,
                   args.save_folder_path,
                   args.final_folder)
