# coding=utf-8

"""
Testing mitsuba renderer - a working example.
"""

import os
import numpy as np
import tqdm
import time
import mitsuba as mi
import vtk
import vtk.numpy_interface.dataset_adapter as dsa
from vtk.util.numpy_support import vtk_to_numpy
from matplotlib import pyplot as plt
import subprocess
from saramis.mesh.mesh_utils import center_model, get_model_center, get_model_vertices_faces_normals

print(mi.variants())
mi.set_variant("cuda_ad_rgb")

scene = mi.load_file("./saramis/renderers/examples/colon.xml") # Defines the scene
params = mi.traverse(scene)
tex = params["PLYMesh.vertex_texcoords"] # UV coords - necessary for the texture

new_tex = []
for i, item in enumerate(tex):
    if (i%2)==0:
        new_tex.append(item)
    else:
        new_tex.append(1-item)

params["PLYMesh.vertex_texcoords"] = new_tex
params.update()

up = np.array([0, 1, 0])
# Calculate the transformation matrix - we use a look-at vector from
# one point to the next
transform = mi.Transform4f().look_at(origin=np.array([500,0, 0]),
                                       target=np.array([0,0,0]), up=up)

print(transform)
# We assume the light comes from the camera source, so
# update both at the same time
params["PerspectiveCamera.to_world"] = transform
params.update()
params["SpotLight.to_world"] = transform
params.update()
params["SpotLight.intensity.value"] = 100000
params.update()

params["PerspectiveCamera.x_fov"] = 40
params.update()
print(params)

images = []
def process(index):
    image = mi.render(scene, spp=124)
    return image.numpy()

plt.imshow(process(100))
plt.show()






















# path_data = "/home/nina/PhD/ClinicalData/Data/MeshData/Totalsegmentator_dataset" # /home/nina/PhD/ClinicalData/Data/MeshData/Totalsegmentator_dataset, set yours here
mesh_orig = "/media/nina/Expansion/new_colons/s0011/colon/fixed_colons/sin_jitter/interp_curve.ply" # Defines the mesh
scene = mi.load_file("/home/nina/repos/rl_env_nav/new_data/colon_cecum_models.xml") # Defines the scene
params = mi.traverse(scene)
print(params)
vertices = np.loadtxt("/media/nina/Expansion/new_colons/amos_0004/colon/colon/interp_curve.txt",
                      delimiter=",") # Defines the centerline the camera could follow
tex = params["PLYMesh.vertex_texcoords"] # UV coords - necessary for the texture

new_tex = []
for i, item in enumerate(tex):
    if (i%2)==0:
        new_tex.append(item)
    else:
        new_tex.append(1-item)

params["PLYMesh.vertex_texcoords"] = new_tex
params.update()

up = np.array([0, 1, 0])
# Calculate the transformation matrix - we use a look-at vector from
# one point to the next
transform = mi.Transform4f().look_at(origin=np.array(vertices[0]),
                                       target=np.array(vertices[20]), up=up)

print(transform)
# We assume the light comes from the camera source, so
# update both at the same time
params["PerspectiveCamera.to_world"] = transform
params.update()
params["SpotLight.to_world"] = transform
params.update()
params["SpotLight.intensity.value"] = 10000
params.update()
# params["SpotLight.cutoff.value"] = 255
# params.update()
params["PerspectiveCamera.x_fov"] = 40
params.update()
print(params)

images = []
import multiprocessing
def process(index):
    transform = mi.Transform4f().look_at(origin=np.array(vertices[index]),
                                       target=np.array(vertices[index+10]), up=up)
    params["PerspectiveCamera.to_world"] = transform
    params["SpotLight.to_world"] = transform
    params.update()
    image = mi.render(scene, spp=124)
    return image.numpy()
path_data = "/media/nina/Expansion/"
if not os.path.exists(os.path.join(path_data, 'output')):
    os.makedirs(os.path.join(path_data, 'output'))

plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True

# Create x and y data points

# for result in tqdm.tqdm(pool.map(process, range(300),300)):
for i in tqdm.tqdm(range(789)):
    result = process(i)
    # if i == vertices.shape[0]-1:
    #     continue
    plt.imshow(result)
    ax = plt.gca()
    ax.xaxis.set_tick_params(labelbottom=False)
    ax.yaxis.set_tick_params(labelleft=False)

    # Hide X and Y axes tick marks
    ax.set_xticks([])
    ax.set_yticks([])
    plt.savefig(os.path.join(path_data, 'output', 'output_{}.jpg'.format(i)))
    plt.close()


