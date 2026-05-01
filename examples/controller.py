from robotiq.robotiq_gripper import RobotiqGripper
from utils.UR_Functions import URfunctions as URControl

class Controller():
    def __init__(self, robot: URControl, gripper: RobotiqGripper):
        self.robot = robot
        self.gripper = gripper
        
    def fully_open_gripper(self, speed=20, force=255):
        self.gripper.move(self.gripper.get_min_position(), speed, force)
    
    def fully_close_gripper(self, speed=20, force=255):
        self.gripper.move(self.gripper.get_max_position(), speed, force)

    def set_gripper(self, position, speed=20, force=255):
        self.gripper.move(position, speed, force)

    def go_home(self):
        self.robot.go_home()
        
    def move_tcp(self, pose: list[float], vel: float, acc: float):
        self.robot.movej_tcp(pose, vel, acc)
        
    def vial_gripped(self) -> bool:
        print(f"Is Closed: {self.gripper.is_closed()}")
        print(f"Is Open: {self.gripper.is_open()}")
        print(f"Get Closed {self.gripper.get_closed_position()}")
        print(f"Get Current Pos{self.gripper.get_current_position()}")
        print(f"Get Max Pos{self.gripper.get_max_position()}")
        print(f"Get Min Pos{self.gripper.get_min_position()}")
        print(f"{self.gripper.GripperStatus}")
        epsilon = 50

        if self.gripper.get_current_position() >= (self.gripper.get_closed_position() - epsilon):
            return False
        else:
            return True