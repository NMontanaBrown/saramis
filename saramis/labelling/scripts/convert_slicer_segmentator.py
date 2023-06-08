# coding=utf-8

"""
Python script to convert the individual nii files
to seg.nrrd files for editing.
"""

import os
import subprocess

path_script = "/path/to/save_slicer_segmentor_script.py"
path_slicer = "/path/to/3Dslicer"

path_data = ""
folders = os.listdir(path_data)
folders.sort()
for folder in folders:
    path_segs = os.path.join(path_data, folder, "slicer_segs")
    path_save = os.path.join(path_data, folder)

    subprocess.run(["xvfb-run",
                    "-a",
                    path_slicer,
                    "--no-splash",
                    "--no-main-window",
                    "--python-script",
                    path_script,
                    path_segs,
                    path_save,
                    "auto_seg.seg.nrrd"])
