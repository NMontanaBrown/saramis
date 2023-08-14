import os

import numpy as np
import gym

from utils import load_scene, render_scene, check_structure_visible, check_wall_intersection, load_vertices, distance_reward

from copy import deepcopy

class NavigationEnvironment(gym.Env):
   
    def __init__(self, all_cases_path, xml_path, save_trajectory_images=False):
        
        self.all_cases_path = all_cases_path
        self.xml_path = xml_path
        
        self.image_shape = (100, 200, 3, 4) 
        self.camera_step_size = 8
        self.movement_threshold = self.camera_step_size / 4.0
        
        self.case_names = sorted(os.listdir(self.all_cases_path))
        
        self.max_intensity = 10_000.0
        
        self.observation_space = gym.spaces.Box(low=0.0, high=self.max_intensity, shape=self.image_shape, dtype=np.float32) 
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(6,))
        
        self.reset()
        
        self.step_num = 0
        
        self.save_trajectory_images = save_trajectory_images
        self.trajectory_images = []
        
        
    def step(self, action):
        
        camera_position_delta = action[:3] * self.camera_step_size
        self.camera_position += camera_position_delta
        
        delta_target = action[3:]
        
        image = render_scene(self.camera_position, delta_target, self.params, self.up, self.scene)
        observation = np.array(image, dtype=np.float32) 
        
        structure_visible = check_structure_visible(self.camera_position, delta_target, self.structure_vertices)
        wall_intersection = check_wall_intersection(self.camera_position, self.centerline_vertices)
        
        if wall_intersection and structure_visible:
            reward = 1000
            done = True
        elif wall_intersection and not structure_visible:
            reward = -1000
            done = True
        elif not wall_intersection and structure_visible:
            reward = 2000
            done  = True
        elif not wall_intersection and not structure_visible:
            reward = 0
            done = False
        
        structure_location = np.mean(self.structure_vertices, axis=0)
        self.secondary_reward = distance_reward(self.camera_position, structure_location, self.centerline_vertices) * 0.0001
        
        reward += self.secondary_reward
        
        if np.mean(np.abs(camera_position_delta)) < self.movement_threshold:
            reward += -1
        
        if self.step_num == 1024-1 and not structure_visible:
            done = True
            reward += -2000
        self.step_num += 1
            
        if self.save_trajectory_images:
            self.trajectory_images.append(observation)
        
        observation_structure = np.zeros(self.image_shape)
        observation_structure[:, :, :, self.structure_to_pick] = observation
        
        return observation_structure, reward, done, {}
        
    def reset(self):
        
        self.step_num = 0
        self.trajectory_images = []
        
        picked_case = np.random.randint(len(self.case_names))
        
        data_path = os.path.join(self.all_cases_path, self.case_names[picked_case], r'colon/colon')
        
        self.params, self.up, self.scene = load_scene(data_path, self.xml_path)
        
        self.centerline_vertices = load_vertices(data_path, 'interp_curve_transformed_centerline_final_space.txt')
        mesh_vertices = load_vertices(data_path, 'interp_curve.txt')
        
        structures = ['cecum', 'rectum', 'hepatic', 'splenic']
        self.structure_to_pick = np.random.randint(len(structures))
        structure_to_load = structures[self.structure_to_pick]
        
        structure_indices_path = os.path.join(data_path, f'indices_final_mesh_int_{structure_to_load}.txt')
        structure_indices = np.loadtxt(structure_indices_path, dtype=np.int64, converters=float)
        self.structure_vertices = mesh_vertices[structure_indices]
        
        # print(f'Picked case {self.case_names[picked_case]} and structure {structure_to_load}')
        
        start_coords = deepcopy(self.centerline_vertices)[np.random.randint(len(self.centerline_vertices))]
        self.camera_position = start_coords
        
        delta_target = self.action_space.sample()[3:]
        
        image = render_scene(self.camera_position, delta_target, self.params, self.up, self.scene)
        observation = np.array(image, dtype=np.float32) # np.clip(resize(np.array(image), self.image_shape), 0.0, 255.0)
        
        observation_structure = np.zeros(self.image_shape)
        observation_structure[:, :, :, self.structure_to_pick] = observation
        
        return observation_structure
