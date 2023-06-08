# coding=utf-8
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
    path_amos = "/path/to/amos22/amos22-organized-val/" # or amos22-organized-train
    folders = os.listdir(path_amos)
    for folder in folders:
        path_orig = os.path.join(path_amos, folder, "Orig")
        files = os.listdir(path_orig)
        vol = [file for file in files if "label" not in file][0]
        vol_path = os.path.join(path_orig, vol)
        path_save = os.path.join(path_amos, folder, "slicer_segs")
        run_slicer_segmentor(path_total_segmentor, vol_path,  path_save)
