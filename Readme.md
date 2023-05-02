# How to use the project in simple steps

## Step 1 : 
Install Carla as a release or build it inside the Frameworks folder . Currently only the pythonAPIS folder exists inside frameworks for reference on how to place the installation

## Step 2:
Install Anaconda with python version 3.7.16 . Acitvate the environment and install the following packages and dependancies inside this environment. There is a requirements.txt also present inside the Experiments folder for easy setup with pip

networkx
numpy; python_version < '3.0'
numpy==1.18.4; python_version >= '3.0'
distro
Shapely==1.6.4.post2
future
numpy; python_version < '3.0'
numpy==1.18.4; python_version >= '3.0'
pygame
matplotlib
open3d
Pillow
psutil
py-cpuinfo
pygame
python-tr
tornado
Flask
requests


## Step 3: 
Install the CARLA wheel that came with the project. Located inside /Frameworks/CARLA_0.9.14/WindowsNoEditor/PythonAPI/dist into the CONDA environment. This ensures availability of known working carla as a local package . 

## Step 4:
Walk Through DummySingle.ipynb inside Experiments for a full walk through of features
