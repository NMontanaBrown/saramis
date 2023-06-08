# coding=utf-8

"""
Module implementing utilities for parsing
outputs of the VMTK portion of the pipeline
"""

import numpy as np
import os
import json
import csv
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d, splev
from scipy.interpolate import splprep, BSpline

def parse_single_file(filename, header=True):
    """
    For a given filename output from
    3D Slicer VMTK
    read, combine them into one CSV file.
    :param input_filename: str, path to file
    """
    points =[]
    if header:
        points.append("X,Y,Z\n")
    with open(filename) as f:
        lines = f.readlines()
        lines = [line.split(",") for line in lines]
        if os.path.splitext(filename)[1] == ".fcsv":
            for line in lines[4:]:
                points.append(str(float(line[1]))+","+str(float(line[2]))+","+str(float(line[3]))+ "\n")
        elif os.path.splitext(filename)[1] == ".json":
            with open(filename, 'r') as f:
                data = json.load(f)
            cps = data["markups"][0]["controlPoints"]
            for point in cps:
                points.append(str(float(point["position"][0]))+","+str(float(point["position"][1]))+","+str(float(point["position"][2]))+ "\n")

    if os.path.splitext(filename)[1] == ".fcsv":
        ext_repl = ".fcsv"
    else:
        ext_repl = ".mrk.json"
      
    with open(filename.replace(ext_repl, ".csv"), 'w') as f:
        for line in points:
            f.write(line)
    with open(filename.replace(ext_repl, ".csv"), 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def closest_node(node, nodes):
    """
    Find the closest node to a given node.
    """
    nodes = np.asarray(nodes)
    deltas = nodes - node
    dist_2 = np.einsum('ijk,ijk->ij', deltas, deltas)
    return np.unravel_index(np.argmin(dist_2, axis=None), dist_2.shape)

def read_csv(file):
    """
    Read a CSV file.
    """
    with open(file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def read_mrk_json(file):
    """
    Read .mrk.json file,
    output from 3D Slicer.
    """
    with open(file, 'r') as f:
        data = json.load(f)
        cps = data["markups"][0]["controlPoints"]
        points = []
        for point in cps:
            points.append([float(point["position"][0]), float(point["position"][1]), float(point["position"][2])])
    return points


def parse_directory(path_dir):
    """
    For a given directory, find all json files,
    read, combine them into one CSV file.
    :input path_dir:
    :return: None
    """
    arrays = []
    filenames = os.listdir(path_dir)
    filenames = [os.path.join(path_dir, filename) for filename in filenames if os.path.splitext(filename)[1] == ".json"]
    filenames = [path for path in filenames if "start" not in path]
    for i, filename in enumerate(filenames):
        if i == 0:
            arrays.append(parse_single_file(filename, True)[1:])
        else:
            arrays.append(parse_single_file(filename, False))
    filenames = [os.path.join(path_dir, filename.replace(".mrk.json", ".csv")) for filename in filenames]
    with open(os.path.join(path_dir, "colon_centerline.csv"), 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
    return [[[float(y) for y in x] for x in array] for array in arrays]

def euclidean_distance(p1, p2):
    return np.linalg.norm(p1 - p2)

def find_next_segment(start_point, arrays):
    """
    Matching algorithm to find the closest segment
    to a given point.
    :param start_point: np.array, point to match
    :param arrays: np.array, array of arrays
    :return: - line segment, starting from point closest to
    start_point
    """
    endpoints = [[array[0], array[-1]] for array in arrays]
    segments = np.array(endpoints)
    # Find the closest segment to the start point
    array_segments = []
    flip = []
    original_segments = segments
    next_point = start_point
    while len(segments):
        closest_segment = closest_node(next_point, segments)
        if closest_segment[1]:
            flip.append(True)
        else:
            flip.append(False)
        # Remove the closest segment from the list of segments
        closest_segment_original = np.where(np.all(np.all(original_segments == segments[closest_segment[0],
                                                                            ...], axis=1), axis=1))[0][0]
        array_segments.append(closest_segment_original)

        next_point = segments[closest_segment[0], int(not(closest_segment[1])), ...]
        segments = np.delete(segments, closest_segment[0], axis=0)
    
    new_arrays = []
    for i, item in enumerate(array_segments):
        if flip[i]:
            new_arrays.append(arrays[item][::-1])
        else:
            new_arrays.append(arrays[item])
    return np.concatenate(new_arrays)
