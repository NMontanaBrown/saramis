# coding=utf-8

"""

"""

import os
import nibabel as nib
import subprocess
import numpy as np
import nrrd
import vtk
import slicerio
import multiprocessing
import tqdm
from saramis.mesh.filtering import get_segment_names_tuples

path_base = "path/to/dataset/"
path_to_save = "path/to/savetxtfile"
total_folders = os.listdir(path_base)

# pick one here
dataset = "total_segmentator" # "amos", "abdomen1k", "total_segmentator"
if dataset == "total_segmentator":
    folders = [folder for folder in total_folders if "s" in folder]
elif dataset == "amos":
    folders = [folder for folder in total_folders if "amos_" in folder]
elif dataset == "abdomen1k":
    folders = [folder for folder in total_folders if "case_" in folder]

folders.sort()
error_folders = []


for folder in tqdm.tqdm(folders):
    path_base_folder = os.path.join(path_base, folder)
    if dataset == "amos":
        path_base_folder = os.path.join(path_base, folder, "Orig")

    path_new = os.path.join(path_base_folder, "analysis", "auto_seg_filter.npy")
    if not os.path.exists(path_new):
        print("No file for {}".format(folder))
        error_folders.append(folder)
        continue
    path_output = os.path.join(path_base_folder, "full_meshes")
    path_header = os.path.join(path_base_folder, "auto_seg.seg.nrrd")
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    else:
        continue
    segment_names_to_labels, segment_names_tuples = get_segment_names_tuples()
    num_segments = len(segment_names_to_labels)
    _, header = nrrd.read(path_header)
    try:
        seg_new = np.load(path_new)
    except:
        print("Error in {}".format(folder))
        error_folders.append(folder)
        continue

    def process_segment(segment_idx,
                        ):
        """
        Process a single segment.
        """
        num_pixels_new = seg_new == segment_idx
        if np.sum(num_pixels_new) == 0:
            return

        # Define the amount of padding for each dimension
        pad_depth = 1
        pad_height = 1
        pad_width = 1

        # Calculate the new shape of the padded volume
        padded_shape = (
            num_pixels_new.shape[0] + 2 * pad_depth,
            num_pixels_new.shape[1] + 2 * pad_height,
            num_pixels_new.shape[2] + 2 * pad_width
        )

        # Create a new array filled with zeros with the padded shape
        padded_volume = np.zeros(padded_shape)

        # Assign the original volume to the inner part of the padded volume
        padded_volume[pad_depth:-pad_depth, pad_height:-pad_height, pad_width:-pad_width] = num_pixels_new
        path_save = os.path.join(path_output,
                                segment_names_to_labels[segment_idx - 1],
                                "{}.nrrd".format(segment_names_to_labels[segment_idx - 1]))
        if not os.path.exists(os.path.join(path_output, segment_names_to_labels[segment_idx- 1])):
            os.makedirs(os.path.join(path_output, segment_names_to_labels[segment_idx - 1]))
        # Intermediate file
        nrrd.write(path_save, padded_volume.astype(np.float32), header)
        # Re-read
        reader = vtk.vtkNrrdReader()
        reader.SetFileName(path_save)
        reader.Update()
        img = reader.GetOutput()
        space_dirs = header["space directions"]
        img.SetSpacing([space_dirs[0][0], space_dirs[1][1], space_dirs[2][2]])
        # Marching Cubes
        marching_cubes_filter = vtk.vtkDiscreteMarchingCubes()
        marching_cubes_filter.SetInputData(img)
        marching_cubes_filter.SetValue(0, 1)
        marching_cubes_filter.Update()
        polydata = marching_cubes_filter.GetOutput()
        # Write to Ply
        ply_writer = vtk.vtkPLYWriter()
        ply_writer.SetFileName(path_save.replace(".nrrd", ".ply"))
        ply_writer.SetInputData(polydata)
        ply_writer.Write()

    pool = multiprocessing.Pool(processes=10)
    for i in pool.map(process_segment, range(1, num_segments + 1)):
        pass
    pool.close()
    pool.join()

    for segment_idx in range(1, num_segments + 1):
        path_save = os.path.join(path_output,
                                segment_names_to_labels[segment_idx - 1],
                                "{}.nrrd".format(segment_names_to_labels[segment_idx - 1]))
        subprocess.call(["rm", path_save])
    
with open(os.path.join(path_to_save, "error_folders_extraction_{}.txt".format(dataset)), "w") as f:
    for folder in error_folders:
        f.write("{}\n".format(folder))
