# SP1 - TMB - CityScape Logic

## Introduction
This is a semester project building upon another student’s thesis, which involved deploying a Tactile Matrix Box (TMB) on the university campus. The TMB processed data from ArUcO cards (similar to QR codes) placed on a table, using a mounted camera. Our team developed a Python server that received this data and implemented the logic for evaluating the cards using the Tkinter Python library. The system then visualized buildings and evaluation results, projecting them back onto the table using a projector.

## Project goals

There are 2 goals of this project:
- [ ]  Creating a basic documentation for working on and developing the TMB table software created by Jiří Šebele as part of his [diploma thesis](https://dspace.cvut.cz/handle/10467/101139). While working on this project, we discovered that there wasn't any step-by-step guide on how to work with the SDK provided, or that some parts were needlessly complicated ( for us at least ). We will aim to make a comprehensible guide on how to set up the software so that other people working with this device can start implementing their own ideas as soon as possible.
- [ ]  In tandem with the guide, we will also start to develop a basic foundation for our city planning project inspired by [MIT](https://www.youtube.com/watch?v=3jvmoj7pLZU) as decribed in the attached google docs.

---

## Setup Guide
*It is recommended to run our implementation on Linux*  
Disclaimer:
Setting it up on your device might not go smoothly even after following all our instructions. You may have to turn to Stack Overflow or ChatGPT to fix some issues.

### Dependencies
Python libraries:
* *pip3 install python-tuio*
* *pip3 install python-osc*
* *sudo apt install python3-tk*
* *pip install pillow* (if errors pop up *python3 -m pip install --upgrade Pillow*)


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

Changing the tracker IS possible, but you need to change YOUR qpath to thesis-tracker in CMakeCache.txt wherever is the keyword "jamo" - pathway on my local thesis-tracker
* All occurances in the file:
  - thesis_tracker_BINARY_DIR:STATIC=/home/jamo/Desktop/SP1/thesis-tracker
  - thesis_tracker_SOURCE_DIR:STATIC=/home/jamo/Desktop/SP1/thesis-tracker
  - CMAKE_CACHEFILE_DIR:INTERNAL=/home/jamo/Desktop/SP1/thesis-tracker
  - CMAKE_HOME_DIRECTORY:INTERNAL=/home/jamo/Desktop/SP1/thesis-tracker
* Just find your local path to the thesis-tracker folder and rewrite it


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

### Table
* Connect your computer to the projector using an HDMI cable, plug in the charger
* Turn on the projector (with the *-v* switch if needed)
* Turn on the PyServer, drag the Canvas window on the second screen and double click to maximize
