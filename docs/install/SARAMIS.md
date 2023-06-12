# Install For SARAMIS

We describe dependencies to replicate and use SARAMIS.
In future, we will aim to provide a Docker image to simplify this process.

## Registration: CUDA Coherent Point Drift

To enable CUDA Coherent Point Drift, you'll need to install the following repository:

```bash
git clone git@github.com:cmsaliba/coherent_point_drift_cuda.git
cd coherent_point_drift_cuda
mkdir build
cd build
cmake -G "Unix Makefiles" -DCPD_CUDA_GENCODE:STRING="-gencode arch=compute_61,code=sm_61" -DCPD_CUDA_BUILD_CMD:BOOL=TRUE ..
make
```

## Tetrahedral meshing: fTetWild

In order to convert the surfaces into tetrahedral volumes for deformable interaction, we use fTetwild.
To use fTetWild, you'll need to install the following repository:

```bash
git clone https://github.com/wildmeshing/fTetWild.git
cd fTetWild
mkdir build
cd build
cmake ..
make
```

## Other requirements: SARAMIS

```bash
conda env create -n saramis --f saramis.yml
conda activate saramis
```

## Other requirements: RL + Rendering

To replicate navigation experiments + rendering, create a separate conda environment.

```bash
conda env create -n saramis_rl_env_nav --f saramis_rl_env_nav.yml
conda activate saramis_rl_env_nav
```


## Setting up Kubric Rendering Environment

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
