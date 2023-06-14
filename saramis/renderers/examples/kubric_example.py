# coding=utf-8

"""
This is a basic example of how one could use the kubric renderer using
the Blender Backend, with SARAMIS data.
"""

import logging
import kubric as kb
from kubric.renderer.blender import Blender as KubricRenderer


path_to_centered_mesh = "Path/to/global/centered/mesh.ply"
logging.basicConfig(level="INFO")

# --- create scene and attach a renderer to it
scene = kb.Scene(resolution=(256, 256))
renderer = KubricRenderer(scene)

# --- populate the scene with objects, lights, cameras
scene += kb.Cube(name="floor", scale=(1, 1, 1), position=(0, 0, -0.1))
scene += kb.PerspectiveCamera(name="camera", position=(0, 0, -200),
                              look_at=(0, 0, 1))

obj = kb.FileBasedObject(
  asset_id="custom", 
  render_filename=path_to_centered_mesh,
  simulation_filename=None)

scene += obj

# --- render and save the output as pngs
scene.camera.position = (0, 0, -300)
frame = renderer.render_still()
kb.write_png(frame["rgba"], "output/helloworld2.png")
scale = kb.write_scaled_png(frame["depth"], "output/helloworld_depth.png")
logging.info("Depth scale: %s", scale)