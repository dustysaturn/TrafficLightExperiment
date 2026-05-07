from robotiq.robotiq_gripper import RobotiqGripper
from utils.UR_Functions import URfunctions as URControl
from experiment.controller import Controller
from experiment.rack import Rack
from experiment.stirrer import Stirrer
from experiment.detector import ColourDetector
from experiment.enums import VialState, SubtractionMethod
from experiment.vial import Vial
from experiment.data_analysis import graph_results
import time
import numpy as np
import cv2

HOST = "192.168.0.2"
ROBOT_PORT = 30003
GRIPPER_PORT = 63352
STIRRER_PORT = "/dev/ttyACM0"
VIAL_CAMERA_PORT = 0
MAIN_CAMERA_PORT = 2

REQUIRED_FRAMES = 100
VISION_TIMEOUT = 60

class TrafficLight():
    def __init__(self) -> None:
        self.robot = URControl(HOST, ROBOT_PORT)
        
        self.gripper = RobotiqGripper()
        self.gripper.connect(HOST, GRIPPER_PORT)
        
        self.controller = Controller(self.robot, self.gripper)
        
        self.detector = ColourDetector(VIAL_CAMERA_PORT, SubtractionMethod.KNN)
        
        self.detector.change_state("Idle")

    def setup_starting_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float], bottom_right_tcp: list[float]) -> None:
        self.starting_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp, bottom_right_tcp, empty=False)
    
    def setup_finishing_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float], bottom_right_tcp: list[float]) -> None:
        self.finishing_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp, bottom_right_tcp, empty=True)
        
    def setup_stirrer(self, stirring_position):
        self.stirrer = Stirrer(stirring_position)
        self.stirrer.connect(STIRRER_PORT)
        
    def setup_volumes(self, volumes):
        self.volumes = volumes
                
    def waitForColour(self, second_run: bool=False) -> tuple[str, float]:
        print(f"Watching for colour change")
        start_time = time.time()
        red_frames = 0
        green_frames = 0
        while(time.time() - start_time < VISION_TIMEOUT):
            current = self.detector.colourName
                        
            if current == "Red":
                red_frames += 1
            else:
                red_frames = 0
                
            if current == "Green":
                green_frames += 1
            else:
                green_frames = 0
                
            duration = time.time() - start_time
            
            if not second_run:
                if red_frames > REQUIRED_FRAMES:
                    return ("Red", duration)
            
            if green_frames > REQUIRED_FRAMES:
                return ("Green", duration)
        
        return ("None", VISION_TIMEOUT)
                                
    def run(self, vials):
        self.vial_results = []
        self.detector.start()
        self.detector.change_state("Going home")
        self.controller.go_home()
        self.controller.set_gripper(91)
        
        while search_position := self.starting_rack.get_next_search_position(): 
            if len(self.vial_results) >= vials:
                break

            row, col = search_position
                        
            self.detector.change_state("Searching for vial in next position")
            self.starting_rack.print_state()
            self.finishing_rack.print_state()

            # Move above that position
            above_position = self.starting_rack.get_above_tcp(row, col, 0.1)
            self.controller.move_tcp(above_position, 1.0, 1.0)
            
            # Move down to that position
            picking_position = self.starting_rack.get_picking_tcp(row, col)
            self.controller.move_tcp(picking_position, 0.2, 0.2)
            
            # Close gripper
            self.controller.fully_close_gripper()
            time.sleep(1)
            
            self.controller.move_tcp(above_position, 1.0, 1.0)
            self.starting_rack.set_vial_state(row, col, VialState.EMPTY)

            if not self.controller.vial_gripped():
                self.detector.change_state("Vial not found")
                self.controller.set_gripper(91)
                time.sleep(1)            
            else:                         
                vial = Vial(self.volumes.get((row, col)), (row, col))

                # Move to above stirrer
                self.detector.change_state("Vial found. Moving to stirrer")
                above_stirrer = self.stirrer.get_above_stirring_position(0.05)
                self.controller.move_tcp(above_stirrer, 1.0, 1.0)
                
                # Move down to just above stirrer
                self.controller.move_tcp(self.stirrer.get_stirring_position(), 1.0, 1.0)
                
                self.detector.vialPresent = True
                time.sleep(1)
                
                self.detector.change_state("Starting stirring")
                self.stirrer.on()
                self.stirrer.set_speed(rpm=1500)
                    
                self.detector.change_state("Monitoring for red or green colour")
                        
                (colour, duration) = self.waitForColour()
                
                if colour == "Red":
                    self.detector.change_state("Detected red")
                    vial.set_yellow_to_red(duration)
                    self.detector.change_state("Monitoring for green colour")
                    (colour, duration) = self.waitForColour(second_run = True)

                if colour == "Green":
                    self.detector.change_state("Detected green")
                    vial.set_yellow_to_green(duration)
                                        
                else:
                    self.detector.change_state("No change detected")
                                        
                self.detector.change_state("Stopping stirrer")
                self.stirrer.off()
                                
                empty_spot = self.finishing_rack.get_empty_spot()

                if not empty_spot:
                    self.detector.change_state("No empty spot available. Stopping")
                    return
                else:
                    self.detector.change_state("Placing vial in finishing rack")
                    # Move to above final spot
                    above_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.1)
                    self.controller.move_tcp(above_position, 0.5, 0.5)
                    
                    # Intermediate movements
                    above_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.07)
                    self.controller.move_tcp(above_position, 0.5, 0.5)

                    intermediate_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.04)
                    self.controller.move_tcp(intermediate_position, 0.5, 0.5)

                    intermediate_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.01)
                    self.controller.move_tcp(intermediate_position, 0.1, 0.1)

                    intermediate_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.005)
                    self.controller.move_tcp(intermediate_position, 0.1, 0.1)
                    
                    # Release gripper
                    self.controller.set_gripper(91)
                    self.finishing_rack.set_vial_state(*empty_spot, VialState.PRESENT)
                    
                    # Update vial
                    vial.switch_rack()
                    vial.set_coords(empty_spot)
                    self.vial_results.append(vial)
                    
                    # Move back up
                    self.controller.move_tcp(above_position, 1.0, 1.0)

        self.detector.running = False
        time.sleep(0.2)

        graph_results(self.vial_results, self.detector.getFolder(), VISION_TIMEOUT)

        self.detector.end()         
        self.stirrer.disconnect()
        self.gripper.disconnect()
        self.robot.close_connection()
    
#org = 0.027018555500000006    