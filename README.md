# AAU_ROB_P2
This repository gives access to the code used in the P2-project at AAU for robotics.
## services
The service-folder contains the code for running the order_service.py, which is a RESTful API. To run the order_service.py, the dependencies written in the requirements.txt file. order_service.py uses the fastapi-library. To run it, run the command:
```console
uvicorn order_service:app
```
## web-gui
The web-gui directory contains code for running the gui. The gui is written in react, with tailwindcss as an alternative for writting css. To run the gui, install node, change directory into web-gui and run:
```console
npm install .
```
This will install the dependencies for the web gui. To run a local instance of the web gui:
```console
npm run dev
```
## fixture.cpp
fixture.cpp is flashed to a ESP32, which controls a LED on the drillhouse and the TOF-sensors on the fixtures.

## kinematics_ur5.py
This code is used to verify the forward and inverse kinematics written the paper. To get different solutions for the inverse kinematics, remove "#" from the commented out variables for theta 1, 3, 5.
