# coding = utf-8

"""
Script to convert the .ply files
into centered files, in
patient frame-of-reference/global and
organ/local frame-of-reference.
"""

import os
import vtk
import vtk.numpy_interface.dataset_adapter as dsa
from vtk.util.numpy_support import vtk_to_numpy
import sksurgeryvtk.models.vtk_surface_model as sm
import numpy as np
import sksurgeryvtk.widgets.vtk_overlay_window as ow
import sksurgerycore.algorithms.procrustes as p
from sksurgeryvtk.utils.matrix_utils import create_matrix_from_list
import multiprocessing
import tqdm

path_base = "path/to/data/"
dataset = "amos" # "total_segmentator", "abdomen1k", "amos"
total_folders = os.listdir(path_base)
if dataset == "total_segmentator":
    total_folders = [folder for folder in total_folders if "s" in folder]
elif dataset == "amos":
    total_folders = [folder for folder in total_folders if "amos_" in folder]
elif dataset == "abdomen1k":
    total_folders = [folder for folder in total_folders if "case_" in folder]
total_folders.sort()

for folder in total_folders:
    path_base_dataset = os.path.join(path_base, folder)
    if dataset == "amos":
        path_base_dataset = os.path.join(path_base, folder, "Orig")
    meshes = os.listdir(os.path.join(path_base_dataset, "full_meshes"))
    lx_t = []
    ly_t = []
    lz_t = []

    def process_mesh_local(mesh):
    # for mesh in meshes:
        path_file = os.path.join(path_base_dataset, "full_meshes", mesh, mesh+"_laplace_smooth_mesh_decimation.ply")
        if not os.path.exists(path_file):
            return None, None, None
        model = sm.VTKSurfaceModel(path_file, [1.0, 1.0, 1.0])
        trans = vtk.vtkMatrix4x4()
        trans.Identity()
        bounding_box = model.actor.GetBounds()
        l_x = (bounding_box[1] + bounding_box[0]) / 2.0
        l_y = (bounding_box[3] + bounding_box[2]) / 2.0
        l_z = (bounding_box[5] + bounding_box[4]) / 2.0
        trans.SetElement(0, 3, -l_x)
        trans.SetElement(1, 3, -l_y)
        trans.SetElement(2, 3, -l_z)
        model.set_model_transform(trans)
        writer = vtk.vtkPLYWriter()
        writer.SetFileName(path_file.replace(".ply", "_centered_local.ply"))
        writer.SetInputConnection(model.transform_filter.GetOutputPort())
        writer.Write()
        lx_t.append([bounding_box[1],bounding_box[0]])
        ly_t.append([bounding_box[3],bounding_box[2]])
        lz_t.append([bounding_box[5],bounding_box[4]])
        return [bounding_box[1],bounding_box[0]], [bounding_box[3],bounding_box[2]], [bounding_box[5],bounding_box[4]]
    lx_t, ly_t, lz_t = [], [], []
    pool = multiprocessing.Pool(processes=8)
    for lx, ly, lz in tqdm.tqdm(pool.imap(process_mesh_local, meshes), total=len(meshes)):
        if lx is None:
            continue
        lx_t.append(lx)
        ly_t.append(ly)
        lz_t.append(lz)
    pool.close()
    pool.join()

    lx_t = np.array(lx_t).mean()
    ly_t = np.array(ly_t).mean()
    lz_t = np.array(lz_t).mean()
    def process_mesh_global(mesh):
        path_file = os.path.join(path_base_dataset, "full_meshes", mesh, mesh+"_laplace_smooth_mesh_decimation.ply")
        if not os.path.exists(path_file):
            return None
        model = sm.VTKSurfaceModel(path_file, [1.0, 1.0, 1.0])
        trans = vtk.vtkMatrix4x4()
        trans.Identity()
        trans.SetElement(0, 3, -lx_t)
        trans.SetElement(1, 3, -ly_t)
        trans.SetElement(2, 3, -lz_t)
        model.set_model_transform(trans)
        writer = vtk.vtkPLYWriter()
        writer.SetFileName(path_file.replace(".ply", "_centered_global.ply"))
        writer.SetInputConnection(model.transform_filter.GetOutputPort())
        writer.Write()
    pool = multiprocessing.Pool(processes=8)
    for _ in tqdm.tqdm(pool.imap(process_mesh_global, meshes), total=len(meshes)):
        pass
    pool.close()
    pool.join()
