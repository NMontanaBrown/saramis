# coding=utf-8

"""
Script to extract Abdomen-1k dataset.
"""

import os
import subprocess

def run_slicer_segmentor(path_total_segmentor, file, save_path):
    """
    Pipeline that runs a full segmentor process,
    saves all the organs as individual .nii.gz files,
    and also saves the segmentation as a .nrrd file for inspection.
    """
    subprocess.run(["python", path_total_segmentor, "-i", file, "-o", save_path])


if __name__ == "__main__":
    path_total_segmentor = "/path/to/Slicer-5.2.1-linux-amd64/lib/Python/bin/TotalSegmentator.py"
    path_abdomen = "/path/to/abdomen1k"
    folders = os.listdir(path_abdomen)
    folders.sort()
    for folder in folders:
        path_orig = os.path.join(path_abdomen, folder)
        files = os.listdir(path_orig)
        vol = [file for file in files if "0000.nii.gz" in file][0]
        vol_path = os.path.join(path_orig, vol)
        path_save = os.path.join(path_abdomen, folder, "slicer_segs")
        if not os.path.exists(path_save):
            os.makedirs(path_save)
            print(folder)
        run_slicer_segmentor(path_total_segmentor, vol_path,  path_save)
