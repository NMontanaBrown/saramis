# Setting up Kubric Rendering Environment

Based on: https://github.com/google-research/kubric/issues/224

First, set up NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

Then, build docker images.

```bash
git clone https://github.com/NMontanaBrown/kubric.git
cd kubric
docker build -f docker/Blender.Dockerfile -t kubricdockerhub/blender:latest .  # build a blender image first
python setup.py bdist_wheel
docker build -f docker/Kubruntu.Dockerfile -t kubricdockerhub/kubruntu:latest .  # then build a kubric image of which base image is the blender image above
```
