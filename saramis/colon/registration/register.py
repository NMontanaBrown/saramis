# coding=utf-8

"""
Functions to register data
"""
import argparse
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from scipy.spatial import cKDTree
from functools import partial
from typing import List
import matplotlib.pyplot as plt


def find_closest_point(points_fixed, points_moving, points_fixed_cls):
    """
    Find the closest points to the points_fixed indexed by
    points_fixed_cls on the points_moving point cloud.
    """
    tree = cKDTree(points_moving)
    return tree.query(points_fixed[points_fixed_cls, :])[1]


def find_closest_point_radius(points_fixed, points_moving, points_fixed_cls, r):
    """
    Find the closest points to the points_fixed indexed by
    points_fixed_cls on the points_moving point cloud
    in a radius r
    :return: list of indices
    """
    tree = cKDTree(points_moving)
    closest_indices = tree.query_ball_point(points_fixed[points_fixed_cls, :], r)
    # Concatenate all lists into a single list
    closest_indices = np.concatenate(closest_indices).tolist()
    # Convert into a set
    closest_indices = list(set(closest_indices))
    return closest_indices