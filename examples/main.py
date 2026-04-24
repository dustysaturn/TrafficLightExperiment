from robotiq.robotiq_gripper import RobotiqGripper
from utils.UR_Functions import URfunctions as URControl
from controller import Controller
from rack import Rack, VialState
from stirrer import Stirrer
from detector import ColourDetector, SubtractionMethod
import time

STARTING_TOP_LEFT = [0.247303237, -0.50343651, 0.061092968, -0.000494386386, 3.10905968, 0.0322229148]
FINISHING_TOP_LEFT = [-0.202857386, -0.519052008, 0.0701338522, -0.000535411239, 3.10906964, 0.032215583]
FINISHING_BOTTOM_RIGHT = [-0.201603630, -0.600121052, 0.0584810206, -0.000566768370, 3.10907973, 0.0322309248]
STIRRER = [0.01291479, -0.49279505,  0.14928015, -0.68575716, -3.05472425,  0.06999038]

HOST = "192.168.0.2"
ROBOT_PORT = 30003
GRIPPER_PORT = 63352

class BlueBottle():
    def __init__(self) -> None:
        self.robot = URControl(HOST, ROBOT_PORT)
        
        self.gripper = RobotiqGripper()
        self.gripper.connect(HOST, GRIPPER_PORT)
        
        self.controller = Controller(self.robot, self.gripper)
        
        self.detector = ColourDetector("./examples/colour_change.mp4", SubtractionMethod.KNN)

    def setup_starting_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float]) -> None:
        self.starting_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp, empty=False)
    
    def setup_finishing_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float], bottom_right_tcp: list[float]) -> None:
        self.finishing_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp, bottom_right_tcp, empty=True)
        
    def setup_stirrer(self, stirring_position):
        self.stirrer = Stirrer(stirring_position)
        self.stirrer.connect()
    
    def run(self):
        self.detector.start()
        self.controller.go_home()
        self.controller.set_gripper(91)

        # self.finishing_rack.set_vial_state(0, 0, VialState.PRESENT)
        # self.finishing_rack.set_vial_state(0, 1, VialState.PRESENT)
        
        while search_position := self.starting_rack.get_next_search_position(): 
            self.starting_rack.print_state()
            self.finishing_rack.print_state()

            # move above that position
            above_position = self.starting_rack.get_above_tcp(*search_position, 0.1)
            self.controller.move_tcp(above_position, 0.1, 0.1)
            
            # move down to that position
            picking_position = self.starting_rack.get_picking_tcp(*search_position)
            self.controller.move_tcp(picking_position, 0.1, 0.1)
            
            # close gripper
            self.controller.fully_close_gripper()
            time.sleep(2)
            
            # move back up
            self.controller.move_tcp(above_position, 0.1, 0.1)

            self.starting_rack.set_vial_state(*search_position, VialState.EMPTY)

            if not self.controller.vial_gripped():
                self.controller.set_gripper(91)
                time.sleep(2)            
            else:                
                # Move to above stirrer
                above_stirrer = self.stirrer.get_above_stirring_position(0.05)
                self.controller.move_tcp(above_stirrer, 0.1, 0.1)
                
                # Move down to just above stirrer
                self.controller.move_tcp(self.stirrer.get_stirring_position(), 0.1, 0.1)
                
                self.detector.vialPresent = True
                self.stirrer.set_speed(rpm=1)
                self.stirrer.start()
                
                # ACTIVE : yellow -> red -> green

                print("Starting stirring.")
                                
                red_frames = 20
                required_frames = 20
                
                while red_frames < required_frames:
                    if self.detector.colourName == "Red":
                        red_frames += 1
                    else:
                        red_frames = 0
                    
                    time.sleep(0.1)
                    
                print("Reaction has reached red. Speeding up stirrer stirrer...")
                
                self.stirrer.set_speed(rpm = 1000)
                green_frames = 20
                
                while green_frames < required_frames:
                    if self.detector.colourName == "Green":
                        green_frames += 1
                    else:
                        green_frames = 0
                    
                    time.sleep(0.1)

                print("Reaction has reached green. Stopping stirrer...")

                self.stirrer.stop()
                
                # PASSIVE: green -> red -> yellow
                print("Waiting until solution is yellow...")
                yellow_frames = 20

                while yellow_frames < required_frames:
                    if self.detector.colourName == "Yellow":
                        yellow_frames += 1
                    else:
                        yellow_frames = 0
                        pass
                    
                    time.sleep(0.1)

                empty_spot = self.finishing_rack.get_empty_spot()
                print(empty_spot)

                if not empty_spot:
                    raise Exception("No empty spot available. Stopping.")
                else:
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
                    
                    # move back up
                    self.controller.move_tcp(above_position, 0.1, 0.1)
    
if __name__ == "__main__":
    experiment = BlueBottle()
    experiment.setup_starting_rack(cols=4, rows=2, row_gap=0.04434444625, col_gap=0.0262839015, top_left_tcp=STARTING_TOP_LEFT)
    experiment.setup_finishing_rack(cols=4, rows=1, row_gap=1, col_gap=0.027318555500000006, top_left_tcp=FINISHING_TOP_LEFT, bottom_right_tcp=FINISHING_BOTTOM_RIGHT)
    experiment.setup_stirrer(STIRRER)
    experiment.run()