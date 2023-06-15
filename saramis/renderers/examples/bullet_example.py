# coding=utf-8

"""
Example of how to load a deformable SARAMIS object in
vtk format into pybullet and run a simulation.
"""

import os
import pybullet as p
from time import sleep
import pybullet_data

physicsClient = p.connect(p.GUI)

# p.setAdditionalSearchPath(pybullet_data.getDataPath())

path_vtk = "/Abdomen-1k/case_000001/full_meshes/vertebrae_L5/vertebrae_L5_laplace_smooth_mesh_decimation.vtk"
path_vtk = "/Abdomen-1k/case_000001/full_meshes/vertebrae_L5/vertebrae_L5_laplace_smooth_mesh_decimation.vtk"

p.resetSimulation(p.RESET_USE_DEFORMABLE_WORLD)
p.resetDebugVisualizerCamera(3,-420,-30,[0.3,0.9,-2])
p.setGravity(0, 0, -10)

bunnyId = p.loadSoftBody(path_vtk,
                         simFileName=path_vtk,
                         mass = 3,
                         useNeoHookean = 1,
                         NeoHookeanMu = 180,
                         NeoHookeanLambda = 600,
                         NeoHookeanDamping = 0.01,
                         collisionMargin = 0.006,
                         useSelfCollision = 1,
                         frictionCoeff = 0.5,
                         repulsionStiffness = 800)
p.changeVisualShape(bunnyId, -1, rgbaColor=[1,1,1,1], flags=0)

p.setPhysicsEngineParameter(sparseSdfVoxelSize=0.25)
p.setRealTimeSimulation(0)

while p.isConnected():
  p.stepSimulation()
  p.getCameraImage(320,200)
  p.setGravity(0,0,-10)