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

    def go_home(self):
        self.robot.go_home()
        
    def move_tcp(self, pose: list[float], vel: float, acc: float):
        self.robot.movej_tcp(pose, vel, acc)
        
    def shake_vial(self, time, direction, force):
        pass
        
    def vial_gripped(self) -> bool:
        if self.gripper.is_closed():
            return False
        else:
            return True
