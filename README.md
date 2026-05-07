# Traffic Light Experiment

Automation for the Traffic Light Experiment using a UR5, Robotiq Gripper, IKA RCT Electric Stirrer, and Logitech HD 1080p Webcam, developed for the CHEM504 module at the University of Liverpool. 

## Overview

This repository provides a collection of Python scripts and utilities to interface with:
- **Universal Robots (UR)** robotic arms via socket communication and RTDE (Real-Time Data Exchange)
- **Robotiq grippers** (tested with HAND-E model)
- **IKA RCT Electric Stirrer** via USB
- **Logitech HD 1080p Webcam** via USB

## Repository Structure

```
TrafficLightExperiment/
├── src/                   # Example scripts demonstrating robot control
│   ├── pose_measurements/ # Calculation of rack vial
│   ├── robotiq/           # Robotiq gripper control modules
│   ├── utils/             # UR robot utilities and helper functions
│   └── experiment/        # Execution of automated experiment
└── README.md 
```

## Prerequisites

### Hardware
- Universal Robots robotic arm (configured at IP: `192.168.0.2`)
- Robotiq gripper (HAND-E or compatible model)
- IKA RCT Electric Stirrer with USB interface
- Logitech HD 1080p Webcam with USB interface

### Software Dependencies
```bash
pip install numpy
pip install opencv-python
pip install Pillow
pip install requests
pip install ur-rtde
pip install matplotlib
```

## Core Modules

### 1. UR Robot Control (`utils/UR_Functions.py`)
Main interface for controlling the UR robot:
- **Joint control**: Move robot to specific joint configurations
- **Cartesian control**: Get current TCP (Tool Center Point) position
- **Home positioning**: Return robot to home configuration
- **Real-time data exchange**: RTDE interface for I/O operations

### 2. Robotiq Gripper Control (`robotiq/robotiq_gripper.py`)
Complete gripper control interface:
- **Connection management**: Socket-based communication
- **Activation**: Initialize and activate gripper
- **Position control**: Open/close gripper with precise positioning (0-255)
- **Force and speed control**: Adjust gripper parameters
- **Status monitoring**: Read gripper state and object detection

### 3. RTDE Interface (`utils/rtde.py`)
Real-Time Data Exchange protocol implementation for UR robots.

### 4. Pose Measurements
Data file containing robot pose samples within rack positions in the starting and finishing rack

### 5. Experiment Automation (`experiment/main.py`)
Classes for experiment state tracking and manipulation:
- TrafficLightExperiment
- Controller
- Detector
- Rack
- Stirrer
- Vial
- Gripper

CV analysis of colour change using Background Subtraction and majority pixel counts of colour masks for yellow, red, and green.

Data analysis of time for the experiment to complete for each vial. 

`main.py` is a CLI entry point for running the experiment.

## Quick Start (WITHIN THE CTH LABS)

### 1. Connect to the Robot
Ensure your computer is on the same network as the robot (default IP: `192.168.0.2`).

### 2. Connect to the Stirrer
Ensure the stirrer is in port `/dev/ttyACM0`.

### 3. Connect to the Camera
Ensure the camera is in port 0.

### 4. Setup the chemicals
Prepare your solutions for the Traffic Light Experiment, waiting until they become yellow before starting Step 5. 

### 5. Run main.py
Input the number of vials in the experiment, and the concentration of NaOH in each.

## Configuration

### Default Settings
- **Robot IP**: `192.168.0.2`
- **Robot Port**: `30003` (socket communication)
- **Gripper Port**: `63352`
- **Camera URL**: `http://192.168.0.2:4242/current.jpg?type=color`
- **Camera Port**: `0`
- **Stirrer Port**: `/dev/ttyACM0`

## Safety Notes

⚠️ **Important Safety Guidelines:**
- Always ensure the robot workspace is clear before running commands
- Start with low velocities and accelerations when testing
- Use the robot's emergency stop button if needed
- Test movements with reduced speed first
- Maintain proper safety distance during operation

## License

This codebase is built upon the chem504-2425 repository (see `https://github.com/LARC-Lab/chem504-2425`), portions of which are based on Universal Robots' RTDE interface (see `utils/rtde.py` for copyright notice).

## Additional Resources

- [Universal Robots Documentation](https://www.universal-robots.com/download/)
- [Robotiq Gripper Manual](https://robotiq.com/support)
- [UR RTDE Interface Guide](https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/)