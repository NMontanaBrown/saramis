# coding= utf-8

"""
CLI module that runs a Slicer TotalSegmentator Process.
"""

import os
import slicer
import subprocess
import argparse

def run_slicer_segmentor(path_total_segmentor, file, save_path):
    """
    Pipeline that runs a full segmentor process,
    saves all the organs as individual .nii.gz files,
    and also saves the segmentation as a .nrrd file for inspection.
    :param path_total_segmentor: str, path to TotalSegmentator.py
    :param file: str, path to input CT scan in .nii.gz format.
    :param save_path: str, path to save_folder where individual segments
                      will be saved.
    """
    subprocess.run(["python", path_total_segmentor, "-i", file, "-o", save_path])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_total_segmentor")
    parser.add_argument("file")
    parser.add_argument("save_path")
    args = parser.parse_args()
    run_slicer_segmentor(args.path_label, args.path_save, args.name_save)
