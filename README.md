# SP1 - TMB - CityScape Logic

## Project goals

There are 2 goals of this project:
- [ ]  Creating a basic documentation for working on and developing the TMB table software created by Jiří Šebele as part of his [diploma thesis](https://dspace.cvut.cz/handle/10467/101139). While working on this project, we discovered that there wasn't any step-by-step guide on how to work with the SDK provided, or that some parts were needlessly complicated ( for us at least ). We will aim to make a comprehensible guide on how to set up the software so that other people working with this device can start implementing their own ideas as soon as possible.
- [ ]  In tandem with the guide, we will also start to develop a basic foundation for our city planning project inspired by [MIT](https://www.youtube.com/watch?v=3jvmoj7pLZU) as decribed in the attached google docs.

---

## Setup Guide
*It is recommended to run our implementation on Linux*  
### Dependencies
Python libraries:
* *pip3 install python-tuio*
* *pip3 install python-osc*
* *sudo apt install python3-tk*

Tracker libraries:
* *sudo apt install libopencv-dev*
* *sudo apt install libfmt-dev*
* *sudo apt install libeigen3-dev*

### Tracker
* Download **thesis-tracker.zip** from Trackers repository. The tracker is already built inside of it. This version was used for our project.
* Unzip
* In its repository run the tracker from the terminal by executing:
  - ***./tracker***
* There is also a tracker switch provided to change the input camera
  - ***./tracker -v 2***
### Server
* Download **server** repository
* The contents are:
  - **PyServer_GridVisualization.py** – our "black box" containing input evaluation and input interpretation onto a Python tkinter Canvas
  - helper_files
    - **config.json** - contains objects to which the ArUco codes will be assigned 
    - ConfigParser - parses the config into classes
  - images - images interpreting the objects in the output
* Run the program by executing:
  -  ***python3 PyServer_GridVisualization.py***
* Close the program by pressing ***q***