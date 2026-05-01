from robotiq.robotiq_gripper import RobotiqGripper
from utils.UR_Functions import URfunctions as URControl
import math

positions = {
    'above_stirrer': [1.3575326204299927, -1.5323995065740128, 1.685145680104391, -1.725114484826559, -1.5701654593097132, -0.23105889955629522],
    'start_bottom_left_picking': [1.7178599834442139, -1.2452590030482789, 1.890017334614889, -2.166133543054098, -1.591705624257223, 0.21135152876377106],
    'start_bottom_left_above': [1.718080997467041, -1.4340586525252839, 1.5015929380999964, -1.588924070397848, -1.5898821989642542, 0.20972639322280884],
    'stirrer_picking': [1.3584225177764893, -1.425328404908516, 1.8450635115252894, -1.9676724872984828, -1.5933993498431605, -0.23100454012026006],
}

HOST = "192.168.0.2"
PORT = 30003
GRIPPER_PORT = 63352
STIRRER_PORT = 3

REQUIRED_FRAMES = 100
VISION_TIMEOUT = 30


def degreestorad(list):
     for i in range(6):
          list[i]=list[i]*(math.pi/180)
     return(list)

def to_home(robot):
    joint_state=degreestorad([93.77,-89.07,89.97,-90.01,-90.04,0.0])
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)

    joint_state = [1.6249512434005737, -1.5768629513182582, 1.5893471876727503, -1.5607174153304477, -1.5599454084979456, -0.0014360586749475601]
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)

    joint_state=degreestorad([93.77,-89.07,89.97,-90.01,-90.04,0.0])
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)

def test_upwards_function():
    robot = URControl(ip="192.168.0.2", port=30003)

    # Activate gripper
    gripper=RobotiqGripper()
    gripper.connect(HOST, GRIPPER_PORT)
    gripper.activate()

    to_home(robot)

    robot.move_joint_list(positions['start_bottom_left_picking'])

    gripper.move(200,20,255)

    current_pos = robot.get_current_tcp()
    
    robot.movel_tcp(get_vertical_position(list(current_pos), 0.2), vel=0.1, acc=0.1)

def main():
    test_upwards_function()

def practice():
    #tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #tcp_socket.connect((HOST, PORT))

    robot = URControl(ip="192.168.0.2", port=30003)

    # Activate gripper
    gripper=RobotiqGripper()
    gripper.connect(HOST, 63352)
    gripper.activate()
    print("Gripper activated")

    to_home(robot)

    #Move_to_bottom_left_vial
    #robot.move_joint_list(positions['start_bottom_left_picking'], 0.5, 0.5)

    # Close gripper
   # gripper.move(150,20,255)

    ## Move vertically
    #robot.move_joint_list(positions['start_bottom_left_above'], 0.5, 0.5)

    # Move to stirring plate
   # robot.move_joint_list(positions['above_stirrer'], 0.1, 0.1)

    # Close gripper
   # gripper.move(150,20,255)


    robot.move_joint_list(positions['stirrer_picking'], 0.5, 0.5)
    gripper.move(150,20,255)

if __name__ == '__main__':
    main()

# Bottom left most position on green vial container. Picking position
#[1.7178599834442139, -1.2452590030482789, 1.890017334614889, -2.166133543054098, -1.591705624257223, 0.21135152876377106]
#[ 0.20534168 -0.50419746  0.06185914 -0.09083483 -3.10816354 -0.06877933]

# Vertically above bottom left picking position
#[1.718080997467041, -1.4340586525252839, 1.5015929380999964, -1.588924070397848, -1.5898821989642542, 0.20972639322280884]
#[ 0.20534824 -0.50420874  0.28930523 -0.0908417  -3.10819179 -0.06877159]

# Measurement in stirring plate
#[1.3574137687683105, -1.4571973842433472, 1.891106907521383, -2.006347795526022, -1.5709951559649866, -0.23025256792177373]
#[ 2.32109551e-02 -5.13919852e-01  1.56561336e-01  3.39052151e-02, -3.13795173e+00  1.75484260e-03]

# Directly above stirring plate
#[1.3575326204299927, -1.5323995065740128, 1.685145680104391, -1.725114484826559, -1.5701654593097132, -0.23105889955629522]
#[ 2.32062614e-02 -5.13907485e-01  2.64114987e-01  3.38969526e-02 -3.13796955e+00  1.66064987e-03]

