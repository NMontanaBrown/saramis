import os
import numpy as np
import mitsuba as mi

from scipy.spatial import distance

import xml.etree.ElementTree

from copy import deepcopy

def xml_edit_filenames(data_path, xml_path):
    et = xml.etree.ElementTree.parse(xml_path)
    root = et.getroot()
    for rank in root.iter():
        if rank.tag =='string' and rank.attrib['name'] == 'filename':
            rank.attrib['value'] = os.path.join(data_path, rank.attrib['value'].split('/')[-1])
    et.write(xml_path)
    # print(f'XML updated filenames to the path: {data_path}')

def load_scene(data_path, xml_path):
    # print(mi.variants())
    mi.set_variant("scalar_rgb")
    xml_edit_filenames(data_path, xml_path)
    scene = mi.load_file(xml_path)
    params = mi.traverse(scene)
    tex = params["PLYMesh.vertex_texcoords"]
    new_tex = []
    for i, item in enumerate(tex):
        if (i%2)==0:
            new_tex.append(item)
        else:
            new_tex.append(1-item)
    params["PLYMesh.vertex_texcoords"] = new_tex
    params.update()
    params["SpotLight.intensity.value"] = 100
    params.update()
    params["PerspectiveCamera.x_fov"] = 1000
    params.update()
    
    up = np.array([0, 1, 0])
    
    return params, up, scene

def render_scene(origin, delta_target, params, up, scene):
    target = origin + delta_target 
    transform = mi.Transform4f().look_at(origin=origin, target=target, up=up)
    params["PerspectiveCamera.to_world"] = transform
    params.update()
    params["SpotLight.to_world"] = transform
    params.update()
    image = mi.render(scene, spp=64)
    return image

def check_structure_visible(origin, delta_target, structure_vertices, distance_to_check=50, num_points_to_check=10, sphere_radius=20):
    new_delta_target_fin = delta_target * distance_to_check
    new_delta_targets = []
    for i in range(0, num_points_to_check+1):
        new_delta_targets.append(new_delta_target_fin * (i/num_points_to_check))
    new_targets = origin + new_delta_targets
    structure_point = np.mean(structure_vertices, axis=0)
    distances = []
    for new_target in new_targets:
        distances.append(distance.euclidean(new_target, structure_point))
    structure_visible = (np.array(distances) < sphere_radius).any()
    return structure_visible

def check_wall_intersection(origin, centerline_vertices, centerline_tolerance=15.0):
    new_origin = deepcopy(origin)
    new_centerline_vertices = deepcopy(centerline_vertices)
    nearest_centerline_vertex_index = np.argmin(np.sum(np.abs(new_centerline_vertices - new_origin), axis=-1))
    vertex = deepcopy(centerline_vertices)[nearest_centerline_vertex_index]
    return distance.euclidean(vertex, origin) > centerline_tolerance

def load_vertices(data_path, filename):
    return np.loadtxt(os.path.join(data_path, filename), delimiter=',')

def distance_reward(origin, structure_location, centerline_vertices):
    origin_index = np.argmin(np.sum(np.abs(centerline_vertices - origin), axis=-1))
    structure_index = np.argmin(np.sum(np.abs(centerline_vertices - structure_location), axis=-1))
    distance = np.abs(origin_index - structure_index)
    return len(centerline_vertices) - distance