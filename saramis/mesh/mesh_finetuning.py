# coding=utf-8

"""
Module that contains MeshLab utils to
transform meshes.
"""

import os
import pymeshlab as pmesh

def laplacian_smooth_mesh(path_mesh:str,
                          path_save:str=None,
                          step_smooth_num:int=24,
                          boundary:bool=False,
                          cotangent_weighting_bool:bool=False,
                          selected:bool=False) -> None:
    """
    From a path to a mesh defined in path_mesh,
    a mesh Laplacian smoothing is performed.
    See source docs:
    https://pymeshlab.readthedocs.io/en/latest/filter_list.html?highlight=laplacian#apply_coord_laplacian_smoothing

    :param path_mesh: str, path to mesh
    :param path_save: str, path to save, if None, same path but different end.
    :param step_smooth_num: int, number of smoothing iterations
    :param boundary: bool
    :param cotangent_weighting_bool:
    :param selected:
    """
    mesh = pmesh.MeshSet()
    mesh.load_new_mesh(path_mesh)
    mesh.apply_coord_laplacian_smoothing(stepsmoothnum=step_smooth_num,
                                         boundary=boundary,
                                         cotangentweight=cotangent_weighting_bool,
                                         selected=selected)
    if path_save is None:
        # replace with .ply and
        path_save = os.path.splitext(path_mesh)[0] + "_laplace_smooth.ply"
    mesh.save_current_mesh(path_save)

def hollow_mesh(path_mesh:str,
                path_save:str=None,
                smooth:bool=True):
    """
    Function that hollows a mesh out to a shell
    of it's original mesh.
    :param path_mesh: str, path to mesh.
    :param path_save: str, if None, same path.
    :param smooth: bool, whether or not to smooth the original mesh.
    """
    mesh_orig = pmesh.MeshSet()
    mesh_orig.load_new_mesh(path_mesh)
    if smooth:
        mesh_orig.apply_coord_laplacian_smoothing(stepsmoothnum=24,
                                                boundary=False,
                                                cotangentweight=False,
                                                selected=False)
    mesh_orig.generate_resampled_uniform_mesh(offset=pmesh.Percentage(49))
    mesh_orig.meshing_invert_face_orientation()
    mesh_orig.generate_by_merging_visible_meshes(mergevisible=False,
                                                 deletelayer=True,)
    mesh_orig.save_current_mesh(os.path.splitext(path_mesh)[0]+"_hollow.ply")

def mesh_decimation(path_mesh:str,
                    path_save:str=None):
    """
    Function to perform a mesh decimation
    by quadric edge collapse in MeshLab
    programmatically.
    :param path_mesh: str, path to mesh.
    :param path_save: str, path to save.
    """
    mesh_orig = pmesh.MeshSet()
    mesh_orig.load_new_mesh(path_mesh)
    mesh_orig.meshing_decimation_quadric_edge_collapse()
    if path_save is None:
        # replace with .ply and
        path_save = os.path.splitext(path_mesh)[0] + "_mesh_decimation.ply"
    mesh_orig.save_current_mesh(path_save)
