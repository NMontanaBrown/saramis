# Reproducing SARAMIS

## Installation

The reproduction of the pipeline involves the installation of several pieces of software, as well as the creation of a new conda environment to run scripts included in the SARAMIS repository.
We point readers to `/docs/install/SARAMIS.md` to obtain the full stack of open-source software required, as well as how to create the conda environment.

Furthermore, the TotalSegmentator package must be installed: 


```bash
pip install TotalSegmentator
```

And additionally installed in the Slicer apps (see here for full details: https://github.com/lassoan/SlicerTotalSegmentator#setup)


## Labelling

- The initial CT data was collected by compounding existing datasets of CT scans: Abdomen1k (https://docs.google.com/forms/d/e/1FAIpQLSeuZ3yanPc0E-SxvYD2ZX8eu-BKxxdQT5GQUpyzfUeK39ytow/viewform), AMOS (https://zenodo.org/record/7262581) and TotalSegmentator (https://zenodo.org/record/6802614).
- The data was preliminarily annotated using an open-source deep learning segmentation model trained to predict 104 anatomical classes in CT scans. The open source model is available at https://github.com/wasserth/TotalSegmentator. Given that the TotalSegmentator dataset contains the same labels, and was inspected by a clinical team, we exclude it from the revision process. To obtain access to the model, users must pip install the repository locally.
- To label all the data, or novel CT scans, users may run the script `./saramis/labelling/extract_abdomen1k_slicer_segmentator.py`and `./saramis/labelling/extract_amos_slicer_segmentator.py`. Please ensure that the paths in the script are pointing to the appropriate location of the Slicer install as well as the datasets.

```bash
python ./saramis/labelling/extract_abdomen1k_slicer_segmentator.py
```
```bash
python ./saramis/labelling/extract_amos_slicer_segmentator.py
```

Additionally, the output of TotalSegmentator was converted into a .seg.nrrd node for ease of editing using an additional script. Again, ensure the following script is modified such that the path to `./saramis/labelling/extracting_slicer_segmentator.py` and 3DSlicer reflect local versions.

```bash
python ./saramis/labelling/scripts/convert_slicer_segmentator.py
```

- All the preliminary annotations derived from the AMOS and Abdomen-1k dataset were inspected by a team of 7 trained annotators and 4 radiologists. The full revision protocol is included in the Supplementary Material of the paper, and was performed manually using 3DSlicer.
- Copies of labels prior and further to correction are included for further analysis.

## Meshing and Tetrahedralisation

Once the review phase was concluded, the data was post-processed to obtain the meshes, textures, and tetrahedral volumes. This consisted of several steps.

* Label cleanup: removal of noise in the verified segmentations, consisting of salt-and-pepper removal.

NOTE: Originally, the data was separately saved at different folders, under `new_folder` and `old_folder` to reflect the prior and new labels generated from analysis. For ease of analysis for future research, we have provided the new and old segmentation nodes as `auto_seg.seg.nrrd` and `auto_seg_pre.seg.nrrd` respectively in the same case folder of the released dataset.

```bash
python ./saramis/labelling/scripts/analysis_get_np.py
```

* Meshing: following the label cleanup, the 3D volumes were converted into .ply files using the marching cubes algorithm (vtk.vtkMarchingCubes()). Modify `path_base` to extract the `dataset` of choice.

```bash
python ./saramis/meshes/scripts/meshing/extract_meshes.py
```

* Mesh decimation and smoothing: given the voxel resolution of the original CT scans could vary between 0.5-5+mm in each direction, the meshes are smoothed using Laplacian smoothing to better represent smooth surfaces. Additionally, a mesh decimation is performed; specifically, we perform a quadric edge collapse using an implementation from MeshLab. Modify `path_base` to process the `dataset` of choice.

```bash
python ./saramis/meshes/scripts/meshing/filter_smooth_meshes.py
```

* Tetrahedral volume generation: the algorithm detailed in fTetWild is used to convert .ply files into tetrahedral volumes. Finally, .msh files are converted into .vtk files using gmsh. 
 Modify `path_base` to process the `dataset` of choice. Additionally, ensure `path_ftetwild` points to a local installation of ftetwild, as detailed in the installation docs at `./saramis/docs/install/SARAMIS.md`.


```bash
python ./saramis/meshes/scripts/meshing/generate_volumes.py
```


## Texturing

The 3D meshes were then processed using Blender to obtain normal maps (to texture the surfaces) and diffuse maps (to add colour to the surfaces).
The normal maps and diffuse maps were designed manually under the supervision of a clinician.
Final procedural materials were inspected and verified by a clinician.

In order to shade and texture the files, a .blend file was used with an in built python script, which can be run in blender using the bpy package. 
In order to run the texturing script, one must:

* Open Blender
```bash
cd /path/to/local/blender
./blender
```
* Click 'Open' option, and select the /saramis/blender/saramis.blend file
* Navigate to the scripting tab: (1) in provided image.
* Open the script 'import_ply_and_texture': (2) in provided image.
* Modify the file_path_base to point to the dataset texturing of choice: (3) in provided image
* Run the script by clicking the 'Play' button next to the import_ply_and_texture name: (4) in provided image.

![Blender Screen of Scripting Tabs, with labels 1, 2, 3, 4 showing where to click or modify the script for instructions to texture data](https://github.com/NMontanaBrown/saramis/blob/main/docs/static/blender_instructions.png?raw=true)


## Procedural colon generation
The colon generation script is under the .blend scripting tab, under the name "Text". It can be run by pressing "Run Script" in the text editor.

Two additional scripts are provided, "just_geom", which allows for the import of a txt file such as the interpolated colon files provided with SARAMIS.
This script can be run by pressing "Run Script" in the text editor, and imports the data and applies a given geometry node, which then allows for one to edit/modify the parameters of the geometry node and visualise them prior to running the full generation script.
