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
    return NavigationEnvironment(all_cases_path, xml_path)

vec_env = make_vec_env(env_creator, n_envs=2)

model = PPO("MlpPolicy", vec_env, verbose=1, n_steps=1024, batch_size=128, n_epochs=8)

num_trials = 512
save_model_after = 8

if not os.path.exists(save_path):
    os.mkdir(save_path)

all_steps = []
all_rewards = []

for trial in range(0, num_trials):
    
    print(f'\nTrial {trial} / {num_trials-1}:')
    
    tic = time()
    
    print('\n    Training started')
    
    model.learn(total_timesteps=2048)
    
    steps, rewards = calculate_metrics(env, model, num_episodes=4)
    
    all_steps.append(np.mean(steps))
    all_rewards.append(np.mean(rewards))
    
    plt.figure()
    plt.plot(all_steps)
    plt.savefig(os.path.join(save_path, r'steps.png'))
    
    plt.figure()
    plt.plot(all_rewards)
    plt.savefig(os.path.join(save_path, r'rewards.png'))
    
    toc = time()
    
    print(f'\n    Trial took {(toc-tic) / 60} min')
    
    if trial%save_model_after==0:
        print('\n    Saving model')
        model.save(os.path.join(save_path, f'model_{trial}'))