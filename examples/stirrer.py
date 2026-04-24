class Stirrer:
    def __init__(self, stirring_position):
        self.speed = 0
        self.running = False
        self.stirring_position = list(stirring_position)
        
    def connect(self):
        pass
            
    def get_stirring_position(self):
        return self.stirring_position
        
    def get_above_stirring_position(self, vertical_gap):
        if vertical_gap <= 0:
            raise ValueError("Vertical gap must be positive")
            
        above_stirring = self.stirring_position.copy()
        above_stirring[2] += vertical_gap
        
        return above_stirring
        
    def start(self):
        print("Stirrer started")
        self.running = True

    def stop(self):
        print("Stirrer stopped")
        self.running = False

    def set_speed(self, rpm):
        self.speed = rpm
        print("Stirrer speed set to {rpm} RPM")
        

