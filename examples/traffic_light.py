from robotiq.robotiq_gripper import RobotiqGripper
from utils.UR_Functions import URfunctions as URControl
from controller import Controller
from rack import Rack
from stirrer import Stirrer
from detector import ColourDetector
from enums import VialState, SubtractionMethod
from vial import Vial
import time

HOST = "192.168.0.2"
ROBOT_PORT = 30003
GRIPPER_PORT = 63352
STIRRER_PORT = 3

REQUIRED_FRAMES = 20
VISION_TIMEOUT = 30

class TrafficLight():
    def __init__(self) -> None:
        self.robot = URControl(HOST, ROBOT_PORT)
        
        self.gripper = RobotiqGripper()
        self.gripper.connect(HOST, GRIPPER_PORT)
        
        self.controller = Controller(self.robot, self.gripper)
        
        self.detector = ColourDetector("./examples/colour_change.mp4", SubtractionMethod.KNN)
        
        self.state = "Idle"

    def setup_starting_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float], bottom_right_tcp: list[float]) -> None:
        self.starting_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp, bottom_right_tcp, empty=False)
    
    def setup_finishing_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float], bottom_right_tcp: list[float]) -> None:
        self.finishing_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp, bottom_right_tcp, empty=True)
        
    def setup_stirrer(self, stirring_position):
        self.stirrer = Stirrer(stirring_position)
        self.stirrer.connect(STIRRER_PORT)
        
    def setup_volumes(self, volumes):
        self.volumes = volumes
                
    def waitForColour(self, colourName: str) -> float:
        print(f"Watching for colour change to {colourName}")
        start_time = time.time()
        colour_frames = 0
        while(colour_frames < REQUIRED_FRAMES):
            if(time.time() - start_time > VISION_TIMEOUT):
                self.state = "Colour change not detected."
                return -1
            
            if self.detector.colourName == colourName:
                colour_frames += 1
            else:
                colour_frames = 0        
            time.sleep(0.1)
        
        end_time = time.time() - start_time    
        
        print(f"Solution has reached {colourName}")
        
        return end_time
    
    def run(self):
        self.vial_results = []
        self.detector.start()
        self.state = "Going home"
        self.controller.go_home()
        self.controller.set_gripper(91)
        
        while search_position := self.starting_rack.get_next_search_position(): 
            row, col = search_position
            
            vial = Vial(self.volumes.get((row, col)), (row, col))
            
            self.state = "Searching for vial in next position"
            self.starting_rack.print_state()
            self.finishing_rack.print_state()

            # move above that position
            above_position = self.starting_rack.get_above_tcp(row, col, 0.1)
            self.controller.move_tcp(above_position, 0.1, 0.1)
            
            # move down to that position
            picking_position = self.starting_rack.get_picking_tcp(row, col)
            self.controller.move_tcp(picking_position, 0.1, 0.1)
            
            # close gripper
            self.controller.fully_close_gripper()
            time.sleep(1)
            
            self.controller.move_tcp(above_position, 0.1, 0.1)
            self.starting_rack.set_vial_state(row, col, VialState.EMPTY)

            if not self.controller.vial_gripped():
                self.state = "Vial not found"
                self.controller.set_gripper(91)
                time.sleep(1)            
            else:                         
                # Move to above stirrer
                self.state = "Vial found. Moving to stirrer"
                above_stirrer = self.stirrer.get_above_stirring_position(0.05)
                self.controller.move_tcp(above_stirrer, 0.1, 0.1)
                
                # Move down to just above stirrer
                self.controller.move_tcp(self.stirrer.get_stirring_position(), 0.1, 0.1)
                
                self.detector.vialPresent = True
                
                self.state = "Starting stirring"
                self.stirrer.on()
                self.stirrer.set_speed(rpm=310)
                        
                self.state = "Monitoring for red colour"
                timeToRed = self.waitForColour("Red")
                
                if timeToRed != -1:
                    vial.set_time_to_red(timeToRed)
                    self.state = "Speeding up stirrer"
                    self.stirrer.set_speed(rpm = 1000)

                    print("Stirrer up to speed")
                
                    self.state = "Monitoring for green colour"
                    timeToGreen = self.waitForColour("Green")
                    
                    if timeToGreen != -1:
                        vial.set_time_to_green(timeToGreen)
                
                self.state = "Stopping stirrer"
                print(self.state)
                self.stirrer.off()
                                
                empty_spot = self.finishing_rack.get_empty_spot()

                if not empty_spot:
                    self.state = "No empty spot available. Stopping"
                    raise Exception(self.state)
                else:
                    self.state = "Placing vial in finishing rack"
                    # move to above final spot
                    above_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.1)
                    self.controller.move_tcp(above_position, 0.1, 0.1)
                    
                    # intermediate movements
                    above_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.07)
                    self.controller.move_tcp(above_position, 0.1, 0.1)

                    intermediate_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.04)
                    self.controller.move_tcp(intermediate_position, 0.1, 0.1)

                    intermediate_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.01)
                    self.controller.move_tcp(intermediate_position, 0.1, 0.1)

                    intermediate_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.005)
                    self.controller.move_tcp(intermediate_position, 0.1, 0.1)
                    
                    # # move down to final spot
                    # release_position = self.finishing_rack.get_picking_tcp(*empty_spot)
                    # self.controller.move_tcp(release_position, 0.1, 0.1)

                    # release gripper
                    self.controller.set_gripper(91)
                    self.finishing_rack.set_vial_state(*empty_spot, VialState.PRESENT)
                    
                    vial.switch_rack()
                    vial.set_coords(empty_spot)
                    self.vial_results.append(vial)
                    
                    # move back up
                    self.controller.move_tcp(above_position, 0.1, 0.1)
                    
        self.stirrer.disconnect()
        self.gripper.disconnect()
        self.robot.close_connection()
    
#org = 0.027018555500000006    