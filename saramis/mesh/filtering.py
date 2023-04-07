# coding=utf-8

"""
Module that implements utilities towards filtering and postprocessing segment volumes
"""

import os
import sys
import vtk
import numpy as np
import skimage
import slicerio
import nrrd
import SimpleITK as sitk
import nrrd


def full_segment_to_labels():
    """
    Utility function that returns the list of
    segment label names from TotalSegmentator.
    :return: List[str]
    """
    segment_names_to_labels = [
                    # "background",
                    "spleen",
                    "kidney_right",
                    "kidney_left",
                    "gallbladder",
                    "liver",
                    "stomach",
                    "aorta",
                    "inferior_vena_cava",
                    "portal_vein_and_splenic_vein",
                    "pancreas",
                    "adrenal_gland_right",
                    "adrenal_gland_left",
                    "lung_upper_lobe_left",
                    "lung_lower_lobe_left",
                    "lung_upper_lobe_right",
                    "lung_middle_lobe_right",
                    "lung_lower_lobe_right",
                    "vertebrae_L5",
                    "vertebrae_L4",
                    "vertebrae_L3",
                    "vertebrae_L2",
                    "vertebrae_L1",
                    "vertebrae_T12",
                    "vertebrae_T11",
                    "vertebrae_T10",
                    "vertebrae_T9",
                    "vertebrae_T8",
                    "vertebrae_T7",
                    "vertebrae_T6",
                    "vertebrae_T5",
                    "vertebrae_T4",
                    "vertebrae_T3",
                    "vertebrae_T2",
                    "vertebrae_T1",
                    "vertebrae_C7",
                    "vertebrae_C6",
                    "vertebrae_C5",
                    "vertebrae_C4",
                    "vertebrae_C3",
                    "vertebrae_C2",
                    "vertebrae_C1",
                    "esophagus",
                    "trachea",
                    "heart_myocardium",
                    "heart_atrium_left",
                    "heart_ventricle_left",
                    "heart_atrium_right",
                    "heart_ventricle_right",
                    "pulmonary_artery",
                    "brain",
                    "iliac_artery_left",
                    "iliac_artery_right",
                    "iliac_vena_left",
                    "iliac_vena_right",
                    "small_bowel",
                    "duodenum",
                    "colon",
                    "rib_left_1",
                    "rib_left_2",
                    "rib_left_3",
                    "rib_left_4",
                    "rib_left_5",
                    "rib_left_6",
                    "rib_left_7",
                    "rib_left_8",
                    "rib_left_9",
                    "rib_left_10",
                    "rib_left_11",
                    "rib_left_12",
                    "rib_right_1",
                    "rib_right_2",
                    "rib_right_3",
                    "rib_right_4",
                    "rib_right_5",
                    "rib_right_6",
                    "rib_right_7",
                    "rib_right_8",
                    "rib_right_9",
                    "rib_right_10",
                    "rib_right_11",
                    "rib_right_12",
                    "humerus_left",
                    "humerus_right",
                    "scapula_left",
                    "scapula_right",
                    "clavicula_left",
                    "clavicula_right",
                    "femur_left",
                    "femur_right",
                    "hip_left",
                    "hip_right",
                    "sacrum",
                    "face",
                    "gluteus_maximus_left",
                    "gluteus_maximus_right",
                    "gluteus_medius_left",
                    "gluteus_medius_right",
                    "gluteus_minimus_left",
                    "gluteus_minimus_right",
                    "autochthon_left",
                    "autochthon_right",
                    "iliopsoas_left",
                    "iliopsoas_right",
                    "urinary_bladder"
                ]
    return segment_names_to_labels


def format_labels(input_filename,
                  output_filename,
                  segment_names_to_labels,
                  filter_value=100,
                  ):
    """
    Function that takes a .seg.nrrd file
    that has been edited, and formats to a
    single label.
    :param input_filename: str, path in
    :param output_filename: str, path out
    :param segment_names_to_labels: List[str]
    :param filter_value: int, max size of disconnected islands
                         to filter out of the segmentation.
    """

    segment_names_tuples = [(name, i+1) for i, name in enumerate(segment_names_to_labels)]

    # Read voxels and metadata from a .seg.nrrd file
    voxels, header = nrrd.read(input_filename)
    segmentation_info = slicerio.read_segmentation_info(input_filename)
    # Get selected segments in a 3D numpy array and updated segment metadata
    extracted_voxels, extracted_header = slicerio.extract_segments(voxels, header, segmentation_info, segment_names_tuples)

    # Create new array for refined segments 
    refined_voxels = np.zeros(extracted_voxels.shape, dtype=np.int32)

    for i in range(1, len(segment_names_to_labels)+1):
        # Morphological closing of extracted segments
        morph = sitk.BinaryMorphologicalClosingImageFilter()
        morph.SetForegroundValue(1)
        image = sitk.GetImageFromArray((extracted_voxels.astype(np.int32)==i).astype(np.int32))
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
            intersect = np.logical_and(smoothed_array, refined_voxels)
            if np.sum(intersect) > 0:
                # If intersection exists, set the intersecting voxels to 0
                smoothed_array[intersect] = 0
        # Add refined segments to refined_voxel
        refined_voxels += i*smoothed_array

    # Write refined voxels and metadata to .nii file
    nrrd.write(output_filename, refined_voxels, extracted_header)

def get_skeleton(input_filename,
                 output_filename):
    """
    Skeletonise a .nrrd file.
    :param input_filename: str, path in
    :param output_filename: str, path out.
    """
    # Read voxels and metadata from a .nrrd file
    voxels, header = nrrd.read(input_filename)
    # Skeletonise voxels
    skeleton_voxels = skimage.morphology.skeletonize_3d(voxels)
    skimage.morphology.binary_dilation(skeleton_voxels, footprint=None, out=None)
    skimage.morphology.binary_dilation(skeleton_voxels, footprint=None, out=None)
    skimage.morphology.binary_dilation(skeleton_voxels, footprint=None, out=None)
    # Write skeleton voxels and metadata to .nii file
    nrrd.write(output_filename, 255*skeleton_voxels, header)
