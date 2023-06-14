# How to use the SARAMIS Blender file

We include the Blender file for the procedural texturing of SARAMIS assets, as well as the procedural generation of colons.
The Blender file is located at `saramis/blender/saramis.blend`, and can be opened by using "Open" in Blender (tested on Blender 3.4.1).

Several bpy scripts are included in the .blend file, and can be found in the "Scripting" tab.

## Procedural texturing
The colon generation script is under the .blend scripting tab, under the name "import_ply_and_texture". It can be run by pressing "Run Script" in the text editor.

If you want to visualise the textures and play around with the parameters, the blend file includes a sphere roughly in the dimensionality order of the organs in SARAMIS. By changing onto the "Shading" tab, with the sphere selected, you can see the texture applied to the sphere. The parameters of the texture can be changed in the "Node Editor" tab, under the "Shader Editor" view.

## Procedural colon generation
The colon generation script is under the .blend scripting tab, under the name "Text". It can be run by pressing "Run Script" in the text editor.

Two additional scripts are provided, "just_geom", which allows for the import of a txt file such as the interpolated colon files provided with SARAMIS.
This script can be run by pressing "Run Script" in the text editor, and imports the data and applies a given geometry node, which then allows for one to edit/modify the parameters of the geometry node and visualise them prior to running the full generation script.
