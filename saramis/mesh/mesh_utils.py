# coding=utf-8

"""
Module with functions to read .obj meshes obtained from simulation setup
and output a sphere file for SOFA simulation.
"""

from typing import List
import os
import meshio
import numpy as np
import vtk
import vtk.numpy_interface.dataset_adapter as dsa
from vtk.util.numpy_support import vtk_to_numpy
import sksurgeryvtk.models.vtk_surface_model as sm
import sksurgeryvtk.widgets.vtk_overlay_window as ow
import sksurgerycore.algorithms.procrustes as p
from sksurgeryvtk.utils.matrix_utils import create_matrix_from_list

def write_spheres(filename:str, output_filename:str=None, radius_sphere:int=20):
    """
    Function that takes an input .obj file
    and outputs a .sph file.
    For every vertex in the mesh, we define a sphere of
    r=radius_sphere centered on the vertex.
    This file can be used for collision detection in SOFA.

    :param filename: str, path to .obj file.
    :param output_filename: str, (default=None), path to
                            save file.
    :param radius_sphere: int, (default=20), size of the
                          radius of the collision spheres.
    :return: None
    """
    # Read mesh
    mesh = meshio.read(filename)

    if output_filename is None:
        # We make a file at the same base location as original object
        # with the same name but change the extension.
        base, _ = os.path.splitext(filename)
        output_filename = base + ".sph"

    # Write file
    with open(output_filename, "w") as f:
        f.write("sph 1.0\n")
        f.write("nums {:d}\n".format(len(mesh.points)))
        for i in range(len(mesh.points)):
            f.write("{:s} {:d} {:4.3f} {:4.3f} {:4.3f} {:4.3f}\n".format(
                "sphe",
                i,
                mesh.points[i, 0],
                mesh.points[i, 1],
                mesh.points[i, 2],
                radius_sphere
                ))

def write_indices(filename:str, output_filename:str=None):
    """
    Function that takes an input .txt file
    and outputs a .obj file.
    For every index in the .txt file, we write a line
    in the corresponding .obj file
    This file can be used for collision detection in SOFA.

    :param filename: str, path to .txt file.
    :param output_filename: str, (default=None), path to
                            save file.
    :return: None
    """
    with open(filename) as file:
        lines = [line.rstrip() for line in file]
    name, _ = os.path.splitext(os.path.split(filename)[1])
    if output_filename is None:
        # We make a file at the same base location as original object
        # with the same name but change the extension.
        base, _ = os.path.splitext(filename)
        output_filename = base + ".obj"

    # Write file
    with open(output_filename, "w") as f:
        f.write("o {}\n".format(name))
        for line in lines:
            substr = line.split()
            f.write("{:s} {:i}\n".format(
                "v",
                substr[1], # The indices are formatted in "0 index" notation
                ))

def center_model(path_vtk:str,
                 path_save:str=None,
                 center_vector:list=None):
    """
    Function to take non-normalised VTK model and
    save it such that all vertices are mean-centered
    around zero. If a center_vector is passed,
    the mesh is centered according to that vector.
    :param path_vtk: str, path to vtk file
    :param path_save: str, (default=None) path to save
    :param center_vector: (default=None), List[float], len(3),
                          vector to center the vector to a given
                          Cartesian space. If not passed,
                          it will center it based on the model
                          average center location.
    """
    if path_save is None:
        path_save = os.path.splitext(path_vtk)[0]+"_normalised.vtk"

    # Extract centroid and model.
    model = sm.VTKSurfaceModel(path_vtk)
    trans = vtk.vtkMatrix4x4()
    trans.Identity()
    if center_vector is None:
        bounding_box = model.actor.GetBounds()
        l_x = (bounding_box[1] + bounding_box[0]) / 2.0
        l_y = (bounding_box[3] + bounding_box[2]) / 2.0
        l_z = (bounding_box[5] + bounding_box[4]) / 2.0
    else:
        l_x = center_vector[0]
        l_y = center_vector[1]
        l_z = center_vector[2]

    trans.SetElement(0, 3, -l_x)
    trans.SetElement(1, 3, -l_y)
    trans.SetElement(2, 3, -l_z)
    model.set_model_transform(trans)

    # Save
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(path_save)
    writer.SetInputConnection(model.transform_filter.GetOutputPort())
    writer.Write()

def get_model_vertices_faces_normals(path_ply):
    """
    From path_vtk to .ply object, read the file
    and extract coordinates of surface and
    normals to those points.
    :param path_vtk: str, path to object.
    :return: vertices, np.Array, [N, 3]
             faces, np.Array, [M, 3]
             normals, np.Array, [N, 3]
    """
    reader = vtk.vtkOBJReader()
    reader.SetFileName(path_ply)
    reader.Update()
    polydata = reader.GetOutput()
    # Extract faces and vertices
    vertices = vtk_to_numpy(dsa.WrapDataObject(polydata).Points)
    faces = vtk_to_numpy(dsa.WrapDataObject(polydata).Polygons)
    normals = vtk_to_numpy(polydata.GetPointData().GetNormals())
    return vertices, faces, normals


def slicesampler_2_p2l(pose):
    """
    Function to convert slicesampler output into p2l frame of reference.
    :param pose: np.array, (4,4) homogenous transformation
                    representing slicesampler pose.
    :return: new_pose, np.array, (4,4) homogenous transformation
                of US plane characterization for SL frame of reference.
    """
    new_pose = np.eye(4)
    y_p2l = -pose[0:3, 0]
    z_p2l = pose[0:3, 1]
    x_p2l = np.cross(y_p2l, z_p2l)
    new_pose[:3, 0] = x_p2l
    new_pose[:3, 1] = y_p2l
    new_pose[:3, 2] = z_p2l
    new_pose[:, 3] = pose[:, 3]
    return new_pose

def pose_constructor(normal, point):
    """
    Given a coordinate point, and
    point normal, we define a pose on
    the conventions defined in [1] for simulation
    of US slices.
    :param normal: np.Array, (N, 3), defining normal.
    :param point: np.Array, (N, 3), defining coordinate.
    :return matrix: np.array (N, 4, 4), homogenous transform
                    in slicesampler format.
    References:
    [1]: J. Ramalhinho et al., "Registration of untracked 2D
         laparoscopic ultrasound to CT images of the liver
         using multi-labelled content-based image retrieval",
         DOI: 10.1109/TMI.2020.3045348
    """
    z_im = -np.tile(np.array([1, 0, 0]), (normal.shape[0], 1))
    y_im = -normal
    x_im = np.cross(y_im, z_im)
    matrix = np.tile(np.eye(4), (normal.shape[0], 1, 1))
    matrix[:, 0:3,0] = x_im
    matrix[:, 0:3, 1] = y_im
    matrix[:, 0:3, 2] = z_im
    matrix[:, 0:3, 3] = point
    return matrix

def generate_grid(rot:List[float], d:List[float]=[0, -30.0], steps=List[int]):
    """
    Function that generates an equally spaced grid
    of parameters for a given set of values in
    rot and d.
    :param rot: List[float], len(3) or len(6), rotation parameters
                             in degrees defining rotation around 
                             x, y, axes.
    :param d: List[float], len(2) or len(4), distance to move
              along normal vecotr
    :param steps: List[int], number of steps to take along
                  normal vector.
    :return:
        - grid: List[List[float]], where each sublist is len(6)

    """
    if len(rot) == 3:
        rot = [-rot[0], rot[0],
               -rot[1], rot[1],
               -rot[2], rot[1],]
    elif len(rot) !=6:
        raise ValueError

    if len(d) != 2:
        raise ValueError
    if len(steps) != 4:
        raise ValueError

    rx_grid, ry_grid, rz_grid, d_grid = np.meshgrid(np.linspace(rot[0],
                                                                rot[1],
                                                                steps[0]),
                                                    np.linspace(rot[2],
                                                                rot[3],
                                                                steps[1],
                                                    np.linspace(rot[4],
                                                                rot[5],
                                                                steps[2]),
                                                    np.linspace(d[0],
                                                                d[1],
                                                                steps[3])))
    grid = np.concatenate((np.expand_dims(rx_grid, axis=-1),
                          np.expand_dims(ry_grid, axis=-1),
                          np.expand_dims(rz_grid, axis=-1),
                          np.expand_dims(d_grid, axis=-1)), axis=0).reshape(4, np.multiply(steps)).transpose().tolist()
    return grid

