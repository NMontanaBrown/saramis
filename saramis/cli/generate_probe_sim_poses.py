# coding=utf-8

"""

"""

from typing import List
import argparse
import os
import numpy as np
from sksurgeryvtk.utils.matrix_utils import create_matrix_from_list
import saramis.mesh.mesh_utils as mu

def generate_probe_sim_files(path_vtk:str,
                              path_save:str=None,
                              rot=np.zeros(3),
                              d=np.zeros(2)):
    """
    From a mesh file stored as a .vtk
    in path_vtk, generate homogenous transformations
    at each point on the surface. If sim parameters
    rot, np.array of R_x, R_y, R_z or d, np.array of
    range of depth simulation (in ** mm **) along normal, grid of
    transformations is created for all parameters,
    and applied to the poses.

    :param path_vtk: str, path to 
    :param path_save: str,
    :param rot: np.Array
    :param d: np.Array
    """
    # Check or make save path
    if path_save is None:
        path_save = os.path.dirname(path_vtk)
    else:
        if not os.path.exists(path_save):
            os.makedirs(path_save)

    # Get points, normals
    points, _, normals = mu.get_model_vertices_faces_normals(path_vtk)

    # Generate transform grid, if rot and d exist
    if not (np.equal(rot, np.zeros(3)).all() and np.equal(d, np.zeros(2)).all()):
        # Code to generate grid? TODO
        grid = mu.generate_grid(rot, d)
    else:
        grid = None

    # Generate transforms and save
    for i in range(points.shape[0]):
        pose_i = mu.pose_constructor(np.expand_dims(normals[i, ...], axis=0),
                                     np.expand_dims(points[i, ...], axis=0))
        pose_i_p2l = mu.slicesampler_2_p2l(pose_i[0, ...])
        if grid:
            # Generate the transformations to apply
            # to initial pose.
            for j in range(grid.shape[0]):
                trans = create_matrix_from_list([grid[j][0], grid[j][1], grid[j][2], ])
                pose_modified = trans @ pose_i_p2l
                # Generate and save offset
                np.savetxt(os.path.join(path_save, "pose_{}_{}_{}_{}_{}.txt".format(i,
                                                                                    grid[0],
                                                                                    grid[1],
                                                                                    grid[2],
                                                                                    grid[3])),
                           pose_modified)
        else:
            # Save each file
            np.savetxt(os.path.join(path_save, "pose_{}_0_0_0_0.txt".format(i)), pose_i_p2l)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_vtk")
    parser.add_argument("path_save")
    parser.add_argument("rot")
    parser.add_argument("d")
    args = parser.parse_args()
    generate_probe_sim_files(args.path_vtk,
                             args.path_save,
                              args.rot,
                              args.d)