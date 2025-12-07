# UR Robot Control

Python utilities and examples for controlling Universal Robots (UR) robotic arms with Robotiq grippers, developed for the CHEM504 course.

## Overview

This repository provides a collection of Python scripts and utilities to interface with:
- **Universal Robots (UR)** robotic arms via socket communication and RTDE (Real-Time Data Exchange)
- **Robotiq grippers** (tested with HAND-E model)
- **Wrist-mounted cameras** on UR robots

## Repository Structure

```
chem504-2425/
├── examples/              # Example scripts demonstrating robot control
│   ├── robotiq/          # Robotiq gripper control modules
│   └── utils/            # UR robot utilities and helper functions
└── README.md
```

## Prerequisites

### Hardware
- Universal Robots robotic arm (configured at IP: `192.168.0.2`)
- Robotiq gripper (HAND-E or compatible model)
- Optional: Robotiq wrist camera

### Software Dependencies
```bash
pip install numpy
pip install opencv-python
pip install Pillow
pip install requests
pip install ur-rtde
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

## Example Scripts

### Basic Robot Control

#### `test_robot_home.py`
Move robot to predefined joint configurations:
```python
python examples/test_robot_home.py
```
Demonstrates:
- Converting degrees to radians for joint positions
- Moving to specific joint states (with default velocity=0.5, acceleration=0.5)

#### `test_get_joints.py`
Read current robot state:
```python
python examples/test_get_joints.py
```
Retrieves:
- Current joint positions (radians)
- Current TCP position (x, y, z, rx, ry, rz)

### Gripper Control

#### `test_gripper.py`
Control the Robotiq gripper:
```python
python examples/test_gripper.py
```
Demonstrates:
- Connecting to gripper at port 63352
- Moving gripper with position control

#### `test_position.py`
Combined robot and gripper control:
```python
python examples/test_position.py
```
Shows coordinated movement of robot arm and gripper operation.

### Camera Integration

#### `test_get_image.py`
Capture images from a standard USB camera:
```python
python examples/test_get_image.py
```
Features:
- Live camera preview using OpenCV
- Press SPACE to capture images
- Press ESC to exit

#### `test_robotiq_wrist_camera.py`
Capture images from the Robotiq wrist camera:
```python
python examples/test_robotiq_wrist_camera.py
```
Retrieves images via HTTP from the robot's integrated camera.

## Quick Start

### 1. Connect to the Robot

Ensure your computer is on the same network as the robot (default IP: `192.168.0.2`).

### 2. Basic Usage Example

```python
from utils.UR_Functions import URfunctions as URControl
from robotiq.robotiq_gripper import RobotiqGripper

# Initialize robot connection
robot = URControl(ip="192.168.0.2", port=30003)

# Initialize gripper
gripper = RobotiqGripper()
gripper.connect("192.168.0.2", 63352)

# Move robot to home position
robot.go_home()

# Get current position
joint_positions = robot.get_current_joint_positions()
tcp_position = robot.get_current_tcp()

# Move gripper
gripper.move(position=128, speed=255, force=100)
```

### 3. Joint Movement

```python
import math

def degrees_to_rad(degrees_list):
    return [d * (math.pi / 180) for d in degrees_list]

# Define joint angles in degrees
joint_angles_deg = [93.77, -89.07, 89.97, -90.01, -90.04, 0.0]
joint_angles_rad = degrees_to_rad(joint_angles_deg)

# Move robot
robot.move_joint_list(
    q=joint_angles_rad,  # joint positions
    v=0.5,               # velocity
    a=0.2,               # acceleration
    r=0.05               # blend radius
)
```

## Configuration

### Default Settings
- **Robot IP**: `192.168.0.2`
- **Robot Port**: `30003` (socket communication)
- **Gripper Port**: `63352`
- **Camera URL**: `http://192.168.0.2:4242/current.jpg?type=color`

<!-- ### Home Joint Configuration
Default home position (radians):
```python
[1.636, -1.555, 1.570, -1.571, -1.572, -0.00002]
``` -->

## Safety Notes

⚠️ **Important Safety Guidelines:**
- Always ensure the robot workspace is clear before running commands
- Start with low velocities and accelerations when testing
- Use the robot's emergency stop button if needed
- Test movements with reduced speed first
- Maintain proper safety distance during operation

## License

Portions of this code are based on Universal Robots' RTDE interface (see `utils/rtde.py` for copyright notice).


## Additional Resources

- [Universal Robots Documentation](https://www.universal-robots.com/download/)
- [Robotiq Gripper Manual](https://robotiq.com/support)
- [UR RTDE Interface Guide](https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/)