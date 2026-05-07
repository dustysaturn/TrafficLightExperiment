from experiment.enums import VialColour

class Vial():
    def __init__(self, volume, coords) -> None:
        self.colour = VialColour.YELLOW
        self.history = [VialColour.YELLOW]
        self.yellow_to_red = None
        self.red_to_green = None
        self.yellow_to_green = None
        self.volume = volume
        self.rack = "STARTING"
        self.coords = coords
    
    def switch_rack(self) -> None:
        if self.rack == "STARTING":
            self.rack = "FINISHING"
    
    def set_colour(self, colour: VialColour) -> None:
        if colour != self.colour:
            self.colour = colour
            self.history.append(colour)
    
    def set_naoh_volume(self, volume) -> None:
        self.volume = volume
        
    def set_coords(self, coords: tuple[int, int]):
        self.coords = coords
        
    def set_yellow_to_red(self, time):
        self.yellow_to_red = time
        
    def set_red_to_green(self, time):
        self.red_to_green = time
        
        if self.yellow_to_red:
            self.yellow_to_green = self.yellow_to_red + time
        
    def set_yellow_to_green(self, time):
        self.yellow_to_green = time
        