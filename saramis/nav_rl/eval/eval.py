import os

import numpy as np

from env import NavigationEnvironment

import matplotlib.pyplot as plt

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env

from time import time



# change these paths to point to the Data, xml file and where models need to be saved, respectively
all_cases_path = r'./Data'
xml_path = r'./colon.xml'
save_path = r'./saved_models'

env = NavigationEnvironment(all_cases_path, xml_path)

# check_env(env) # PASSED (no warnings)

def calculate_metrics(env, model, num_episodes):
    fin_steps = []
    fin_rewards = []
    print('\n    Evaluation Starting:')
    for i in range(num_episodes):
        done = False
        step_counter = 0
        rewards = []
        observation = env.reset()
        for j in range(1026):
            action, _states = model.predict(observation)
            observation, reward, done, _ = env.step(action)
            step_counter += 1
            rewards.append(reward)
            if done:
                print(f'\n      Evaluation: Episode {i} / {num_episodes-1}:')
                print(f'          Sum rewards: {np.sum(rewards):.2f}')
                print(f'          Steps: {step_counter}')
                fin_steps.append(step_counter)
                fin_rewards.append(np.sum(rewards))
                break
    return fin_steps, fin_rewards

def env_creator():
    env = NavigationEnvironment(all_cases_path, xml_path)
    env.case_names = env.case_names[0:0+1]
    return env

vec_env = make_vec_env(env_creator, n_envs=2)


model = PPO("MlpPolicy", vec_env, verbose=1, n_steps=1024, batch_size=128, n_epochs=8)

# if loading a pretrained model:
# model = PPO.load(os.path.join(save_path, 'model_2560'), env=vec_env)


# =============================================================================
# random start and end locations
# =============================================================================

num_trials = 100

if not os.path.exists(save_path):
    os.mkdir(save_path)

all_steps = []
all_rewards = []

success_tracker = []

for case_num in range(32):
    
    def env_creator():
        env = NavigationEnvironment(all_cases_path, xml_path)
        env.case_names = env.case_names[case_num:case_num+1]
        return env
    
    vec_env = make_vec_env(env_creator, n_envs=1)

    model = PPO("MlpPolicy", vec_env, verbose=1, n_steps=1024, batch_size=128, n_epochs=8)

    # if loading a pretrained model:
    # model = PPO.load(os.path.join(save_path, 'model_2560'), env=vec_env)
    
    for trial in range(0, num_trials):
                                    
        steps, rewards = calculate_metrics(env, model, num_episodes=1)
        
        steps = np.squeeze(np.array(steps))
        rewards = np.squeeze(np.array(rewards))
        
        if steps > 256 and rewards > 500:
            success_tracker.append(0)
        else:
            success_tracker.append(1)
        
        all_steps.append(np.mean(steps))
        all_rewards.append(np.mean(rewards))

# =============================================================================
# sequential start and end locations using a modified version of the env
# =============================================================================

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
        
    def reset(self, structure_ind=0):
        
        self.step_num = 0
        self.trajectory_images = []
        
        picked_case = np.random.randint(len(self.case_names))
        
        data_path = os.path.join(self.all_cases_path, self.case_names[picked_case], r'colon/colon')
        
        self.params, self.up, self.scene = load_scene(data_path, self.xml_path)
        
        self.centerline_vertices = load_vertices(data_path, 'interp_curve_transformed_centerline_final_space.txt')
        mesh_vertices = load_vertices(data_path, 'interp_curve.txt')
        
        structures = ['cecum', 'rectum', 'hepatic', 'splenic']
        self.structure_to_pick = structure_ind
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


num_trials = 100

if not os.path.exists(save_path):
    os.mkdir(save_path)

all_steps = []
all_rewards = []

success_tracker = []

    
def calculate_metrics(env, model, num_episodes, start_pos=None, structure_ind_to_find=0):
    fin_steps = []
    fin_rewards = []
    print('\n    Evaluation Starting:')
    for i in range(num_episodes):
        done = False
        step_counter = 0
        rewards = []
        if start_pos is None:
            observation = env.reset(structure_ind_to_find)
        else:
            observation = env.reset(structure_ind_to_find)
            env.camera_position = start_pos
            
        for j in range(1026):
            action, _states = model.predict(observation)
            observation, reward, done, _ = env.step(action)
            step_counter += 1
            rewards.append(reward)
            if done:
                print(f'\n      Evaluation: Episode {i} / {num_episodes-1}:')
                print(f'          Sum rewards: {np.sum(rewards):.2f}')
                print(f'          Steps: {step_counter}')
                fin_steps.append(step_counter)
                fin_rewards.append(np.sum(rewards))
                break
    return fin_steps, fin_rewards

for case_num in range(32):
    
    all_perms = []
    for perm_num in range(num_trials):
        perm = np.random.permutation(4)
        all_perms.append(perm)
    
    for perm in all_perms:
        
        env = NavigationEnvironment(all_cases_path, xml_path)
        env.case_names = env.case_names[case_num:case_num+1]

        model = PPO("MlpPolicy", env, verbose=1, n_steps=1024, batch_size=128, n_epochs=8)
        
        # if loading a pretrained model:
        # model = PPO.load(os.path.join(save_path, 'model_2560'), env=vec_env)
        for structure_ind in perm:
            
            last_pos = env.camera_position
            
            steps, rewards = calculate_metrics(env, model, num_episodes=1, start_pos=last_pos, structure_ind_to_find=structure_ind)
            
            steps = np.squeeze(np.array(steps))
            rewards = np.squeeze(np.array(rewards))
            
            if steps > 256 and rewards > 500:
                success_tracker.append(0)
            else:
                success_tracker.append(1)
            
            all_steps.append(np.mean(steps))
            all_rewards.append(np.mean(rewards))