# coding=utf-8

"""
Module that implements conversion from nii files to nrrd seg files in
3D slicer.
"""

import os
import argparse
import subprocess
import slicer
import vtk
import sys


def save_slicer_segmentor_as_nrrd(path_folder, save_path, file_name):
    """
    Function to convert the output of TotalSegmentator
    to a .nrrd file for inspection.
    :param path_folder: str, path to folder with .nii.gz files
    :param save_path: str, path to save the .nrrd file
    :param file_name: str, name of the .nrrd file
    """
    from totalsegmentator.map_to_binary import class_map
    labelValueToSegmentName = class_map["total"]

    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    # Get color node with random colors
    randomColorsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeRandom')
    rgba = [0, 0, 0, 0]

    # Read each candidate file
    for labelValue in labelValueToSegmentName:
        segmentName = labelValueToSegmentName[labelValue]
        labelVolumePath = os.path.join(path_folder, segmentName+".nii.gz")
        if not os.path.exists(labelVolumePath):
            print(labelVolumePath)
            continue

        labelmapVolumeNode = slicer.util.loadLabelVolume(labelVolumePath, {"name": segmentName})

        randomColorsNode.GetColor(labelValue,rgba)
        segmentId = segmentationNode.GetSegmentation().AddEmptySegment(segmentName, segmentName, rgba[0:3])
        updatedSegmentIds = vtk.vtkStringArray()
        updatedSegmentIds.InsertNextValue(segmentId)
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, segmentationNode, updatedSegmentIds)

    slicer.util.saveNode(segmentationNode, os.path.join(save_path, file_name))
    slicer.mrmlScene.Clear(0)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_folder")
    parser.add_argument("save_path")
    parser.add_argument("file_name")
    args = parser.parse_args()
    save_slicer_segmentor_as_nrrd(args.path_folder, args.save_path, args.file_name)
