# coding=utf-8

"""
Script to perform comparisons between
data before and after refinement.
"""

import os
import numpy as np
import slicerio
import nrrd
import SimpleITK as sitk
import skimage
import csv
import tqdm
import scipy
import multiprocessing

def create_numpy_arrays_before_and_after(path_old,
                                         path_new,
                                         save_old,
                                         save_new,
                                         segment_names_tuples,
                                         segment_names_to_labels,
                                         filter_value=20):
    """
    Function that creates numpy arrays for the old and new segmentations.
    :param path_old: str
    :param path_new: str
    :param save_old: str
    :param save_new: str
    :param segment_names_tuples: List[Tuple[str, str]]
    :param segment_names_to_labels: List[str]
    :param filter_value: int
    """
    # Read voxels and metadata from a .seg.nrrd file
    voxels, header = nrrd.read(path_old)
    segmentation_info = slicerio.read_segmentation_info(path_old)
    # Get selected segments in a 3D numpy array and updated segment metadata
    extracted_voxels, _ = slicerio.extract_segments(voxels, header, segmentation_info, segment_names_tuples)
    pixel_vals_old = []
    # Save the numpy array
    for i in range(1, len(segment_names_to_labels)+1):
        num_pixels = np.sum(extracted_voxels==i)
        pixel_vals_old.append(num_pixels)

    np.save(save_old, extracted_voxels)

    # Read voxels and metadata from a .seg.nrrd file
    voxels_new, header_new = nrrd.read(path_new)
    segmentation_info_new = slicerio.read_segmentation_info(path_new)
    # Get selected segments in a 3D numpy array and updated segment metadata
    extracted_voxels_new, _ = slicerio.extract_segments(voxels_new, header_new, segmentation_info_new, segment_names_tuples)
    # Create new array for refined segments 
    refined_voxels = np.zeros(extracted_voxels_new.shape, dtype=np.int32)
    pixel_vals_new = []
    for i in range(1, len(segment_names_to_labels)+1):
        morph = sitk.BinaryMorphologicalClosingImageFilter()
        morph.SetForegroundValue(1)
        image = sitk.GetImageFromArray((extracted_voxels_new.astype(np.int32)==i).astype(np.int32))
        rgsmoothedimage  = morph.Execute(image)
        smoothed_array = sitk.GetArrayFromImage(rgsmoothedimage)

        if filter_value:
            labels = skimage.measure.label(smoothed_array, return_num=False)
            # for each label in labels, if the number of voxels is less than filter_value, set the label to 0
            for label in np.unique(labels):
                if label == 0:
                    continue
                if np.sum(labels == label) < filter_value:
                    smoothed_array[labels == label] = 0
            # Check whether smoothed array intersects with other segments in refined voxels
            try:
                intersect = np.logical_and(smoothed_array, refined_voxels)
                if np.sum(intersect) > 0:
                    # If intersection exists, set the intersecting voxels to 0
                    smoothed_array[intersect] = 0
            except:
                print("error folder:", path_old, path_new)
                return path_old
        num_pixels = np.sum(smoothed_array)
        pixel_vals_new.append(num_pixels)
        # Add refined segments to refined_voxel
        refined_voxels += i*smoothed_array
    # Save the numpy array
    np.save(save_new, refined_voxels)
    return pixel_vals_old, pixel_vals_new, header["space directions"]

def compare_preexisting_arr(path_old,
                            path_new,
                            segment_names_to_labels,
                            path_header):
    """
    Function that compares the data
    if it already exists.
    :param path_old: str
    :param path_new: str
    :param segment_names_to_labels: List[str]
    :param path_header: str
    """
    pixel_vals_old = []
    pixel_vals_new = []
    seg_new = np.load(path_new)
    seg_old = np.load(path_old)
    _, header = nrrd.read(path_header)
    for i in range(1, len(segment_names_to_labels)+1):
        num_pixels_new = np.sum(seg_new==i)
        pixel_vals_new.append(num_pixels_new)
        num_pixels_old = np.sum(seg_old==i)
        pixel_vals_old.append(num_pixels_old)
    return pixel_vals_old, pixel_vals_new, header["space directions"]
