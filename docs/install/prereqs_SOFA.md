# Pre-requisites

```bash
sudo apt update && sudo apt upgrade
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.8-dev
sudo apt install python3.9-dev
sudo apt install python3.8-distutils
sudo apt install python3.9-distutils # or whatever version
```

this includes the configuration files, without which the compilation will be unsuccesfull.

## Install CMake

[https://www.linuxcapable.com/how-to-install-cmake-on-ubuntu-22-04-lts/](https://www.linuxcapable.com/how-to-install-cmake-on-ubuntu-22-04-lts/)

This was tested with CMake version 3.22.1

```bash
# Remove previous cmake versions
sudo apt remove cmake
sudo apt purge --auto-remove cmake
sudo apt-get install build-essential
wget http://www.cmake.org/files/v3.22/cmake-3.22.1.tar.gz
tar xf cmake-3.22.1.tar.gz

cd cmake-3.22.1
./configure
make
# Then to install it to your system finally do 
sudo make install 

# Do this to refresh your console 
hash -r

# Then finally check with
cmake --version
```

## Installing Qt

This was tested with Qt5.

Download the unified installer here: 

[Index of /official_releases/online_installers](https://download.qt.io/official_releases/online_installers/)

You need a Qt account so make one, and probably use under the open source version.

# Installing Sofa

[https://www.sofa-framework.org/community/doc/getting-started/build/linux/](https://www.sofa-framework.org/community/doc/getting-started/build/linux/)

[https://sofapython3.readthedocs.io/en/latest/menu/Compilation.html](https://sofapython3.readthedocs.io/en/latest/menu/Compilation.html)

This was tested with sofa-22.06 and python 3.8.16. Additionally, sofapython3 must be included as a plugin.

```bash
cd software
git clone -b v22.06 https://github.com/sofa-framework/sofa.git sofa-22.06/src
cd /home/usr/software/sofa-22.06/src
```

Pre-reqs

```bash
sudo apt install libopengl0
sudo apt install libboost-all-dev
sudo apt install libpng-dev libjpeg-dev libtiff-dev libglew-dev zlib1g-dev
sudo apt install libeigen3-dev
sudo apt install pybind11-dev
```

Compiled using “CodeBlocks – Unix Makefile”. Ninja works adequately well too.

### CMake Variables
Values:

SOFA_FETCH_SOFAPYTHON3=True

CMAKE_PREFIX_PATH=/home/nina/Qt/5.15.2/gcc_64

Python_EXECUTABLE=/usr/bin/python3.8

Python_INCLUDE_DIRS=/usr/include/python3.8

Python_LIBRARIES=/usr/lib/python3.8

Python_ROOT_DIR=/usr/bin

Might need to check here for the docs on how to run this from a CLI.

[https://github.com/sofa-framework/SofaPython3](https://github.com/sofa-framework/SofaPython3)

To check that the right python has been used (important), you should check that the following text appears (like this or similar)

```bash
Adding plugin SofaPython3
-- Python:
    Version: 3.8.16
    Executable: /usr/bin/python3.8
    Headers: /usr/include/python3.8
    Libraries: /usr/lib64/libpython3.8.so
    User site: /home/nina.local/lib/python3.8/site-packages
-- pybind11:
    Version: 2.6.1
    Config: /usr/share/cmake/pybind11/pybind11Config.cmake
```

Once all of this has run successfully, run generate. This should generate the build files in the build dir.

To build:

```bash
cd /home/usr/software/sofa-22.06/build/
make -j 10 # runs the compilation with 10 threads
```

Once the compilation has finished (could take 20-30mins, depending on number of threads used), install the package.

```bash
cd /home/usr/software/sofa-22.06/build/
cmake --install ./
```

## Using SOFA

Set-up the python path and the sofa root

```bash
conda deactivate
export SOFA_ROOT="/home/nina/software/sofa-22.06/build/install/"
export PYTHONPATH="/home/nina/software/sofa-22.06/build/install/plugins/SofaPython3/lib/python3/site-packages/"
```

and test SOFA:
```bash
/path/to/sofa/build/bin/runSofa
```