from robotiq.robotiq_gripper import RobotiqGripper
from utils.UR_Functions import URfunctions as URControl
from controller import Controller
from rack import Rack, VialState

STARTING_TOP_LEFT = []
FINISHING_TOP_LEFT = []

HOST = "192.168.0.2"
ROBOT_PORT = 30003
GRIPPER_PORT = 63352

class BlueBottle():
    def __init__(self) -> None:
        self.robot = URControl(HOST, ROBOT_PORT)
    
        self.gripper = RobotiqGripper()
        self.gripper.connect(HOST, GRIPPER_PORT)
        
        self.controller = Controller(self.robot, self.gripper)
        
    def setup_starting_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float]) -> None:
        self.starting_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp)
    
    def setup_finishing_rack(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_tcp: list[float]) -> None:
        self.finishing_rack = Rack(rows, cols, row_gap, col_gap, top_left_tcp)
    
    def run(self):
        while search_position := self.starting_rack.get_next_search_position(): 
            # move above that position
            above_position = self.starting_rack.get_above_tcp(*search_position, 0.1)
            self.controller.move_tcp(above_position, 0.1, 0.1)
            
            # move down to that position
            picking_position = self.starting_rack.get_picking_tcp(*search_position)
            self.controller.move_tcp(picking_position, 0.1, 0.1)
            
            # close gripper
            self.controller.fully_close_gripper()
            
            # move backup
            self.controller.move_tcp(above_position, 0.1, 0.1)

            if not self.controller.vial_gripped():
                self.starting_rack.set_vial_state(*search_position, VialState.EMPTY)
                self.controller.fully_open_gripper()                
            else:
                self.starting_rack.set_vial_state(*search_position, VialState.PRESENT)
                
                # TODO move to above stirrer
                
                # TODO move down to just above stirrer
                
                # TODO stirrer driver code
                
                # TODO: Add CV stuff
                
                if not (empty_spot := self.finishing_rack.get_empty_spot()):
                    raise Exception("No empty spot available. Stopping.")
                else:
                    # move to above final spot
                    above_position = self.finishing_rack.get_above_tcp(*empty_spot, 0.2)
                    self.controller.move_tcp(above_position, 0.1, 0.1)
                    
                    # TODO: Add sequence of intermediate movements to reduce effect of arc joint movement
                    
                    # move down to final spot
                    release_position = self.finishing_rack.get_picking_tcp(*empty_spot)
                    self.controller.move_tcp(release_position, 0.1, 0.1)

                    # release gripper
                    self.controller.fully_open_gripper()
                    self.finishing_rack.set_vial_state(*empty_spot, VialState.PRESENT)
                    
                    # move back up
                    self.controller.move_tcp(above_position, 0.1, 0.1)
        
    
if __name__ == "__main__":
    positions = {
        'above_stirrer': [1.3575326204299927, -1.5323995065740128, 1.685145680104391, -1.725114484826559, -1.5701654593097132, -0.23105889955629522],
        'start_bottom_left_picking': [1.7178599834442139, -1.2452590030482789, 1.890017334614889, -2.166133543054098, -1.591705624257223, 0.21135152876377106],
        'start_bottom_left_above': [1.718080997467041, -1.4340586525252839, 1.5015929380999964, -1.588924070397848, -1.5898821989642542, 0.20972639322280884],
        'stirrer_picking': [1.3584225177764893, -1.425328404908516, 1.8450635115252894, -1.9676724872984828, -1.5933993498431605, -0.23100454012026006],
        'test': [1.718080997467041, -1.4340586525252839, 1.5015929380999964, -1.588924070397848, -1.5898821989642542, 0.20972639322280884],
    }

    experiment = BlueBottle()
    experiment.setup_starting_rack(4, 2, 1, 1, STARTING_TOP_LEFT)
    experiment.setup_finishing_rack(4, 1, 1, 1, STARTING_TOP_LEFT)
    experiment.run()

# Parameters for experiment
# Optional: 
# - Number of vials 
#
# Required:
# - start rack x
# - start rack y
# - start rack top left
# - end vial x
# - end vial y
# - end rack top left
# - stirrer position