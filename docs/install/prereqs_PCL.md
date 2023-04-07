# Installing PCL and Mesh utilities

<aside>
💡 These are the steps required to set up a machine to process meshes and perform the deformation simulation. This has been set up for an ubuntu machine 22.04. Also, would recommend following the “Install Sofa and SofaPython3” prior to this guide,.

</aside>


# Pre-requisites

Need Qt5 - check exists. Also need some extra pre-requisites.

```bash
ls /usr/lib/x86_64-linux-gnu/cmake/Qt5
```

```bash
sudo apt-get install qttools5-dev libqt5x11extras5-dev qtmultimedia5-dev
```

## Installing VTK

Get VTK 9.2.5

```bash
cd /home/usr/software && mkdir VTK && cd VTK
wget https://www.vtk.org/files/release/9.2/VTK-9.2.5.tar.gz
tar xvf VTK-9.2.5.tar.gz
cd VTK-9.2.5 && mkdir build
```

Make VTK using cmake.

```bash
sudo cmake --install . #(installs to /usr/local)
```

# Libraries

## Install PCL

Get the library:

```bash
cd /home/usr/software && wget https://github.com/PointCloudLibrary/pcl/releases/download/pcl-1.13.0/source.tar.gz
tar xvf pcl.tar.gz
cd pcl && mkdir build
```

With CMake, ensure the following are enabled

```
VTK_Group_Qt       ON
VTK_QT_VERSION     5 # default
QT5_DIR            /usr/lib/x86-64-linux-gnu/cmake/Qt5

VTK_RENDERING_BACKEND OpenGL2 # default
BUILD_SHARED_LIBS  ON
CMAKE_BUILD_TYPE   Release
CMAKE_INSTALL_PREFIX /usr/local
```

and finally, install it

```bash
sudo cmake --install . #(installs to /usr/local)
```

## Install TetGen (1.5.1)

This needs to be downloaded manually as you need to verify your usage:

[https://wias-berlin.de/software/tetgen/download2.jsp](https://wias-berlin.de/software/tetgen/download2.jsp)

Compile it using CMake.

## Install MeshLab

From the Linux snap store, one can get the meshLab app.

## Install ParaView

Just needs downloading:

```bash
cd /home/usr/software/
wget https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.11&type=binary&os=Linux&downloadFile=ParaView-5.11.0-MPI-Linux-Python3.9-x86_64.tar.gz
tar xvf ParaView-5.11.0-MPI-Linux-Python3.9-x86_64.tar.gz
```

Run using:

```bash
/home/usr/software/ParaView/ParaView-5.11.0-MPI-Linux-Python3.9-x86_64/bin/paraview
```

## Installing Blender

Needed for mesh editing. Download it here and install:

https://www.blender.org/download/
