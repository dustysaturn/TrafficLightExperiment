from serial import Serial
import time

MIN_SPEED = 0
MAX_SPEED = 1500

class Stirrer:
    def __init__(self, stirring_position):
        self.speed = 100
        self.running = False
        self.stirring_position = stirring_position.copy()
                    
    def get_stirring_position(self):
        return self.stirring_position
        
    def get_above_stirring_position(self, vertical_gap):
        if vertical_gap <= 0:
            raise ValueError("Vertical gap must be positive")
            
        above_stirring = self.stirring_position.copy()
        above_stirring[2] += vertical_gap
        
        return above_stirring
    
    def _send(self, message):
        self.ser.write(message.encode())
        print(f"Sending {message}")
   
    def connect(self, port):
        self.ser = Serial(port, 9600, timeout=1)
        print(f"Connected on port {port}")

    def disconnect(self):
        self.ser.close()
        print(f"Disconnected stirrer")

    def on(self):
        self._send("START_4\r\n")
        
        self.running = True
        print("Stirrer started")

    def off(self):
        self._send("STOP_4\r\n")
        
        self.running = False
        print("Stirrer stopped")

    def set_speed(self, rpm: int):
        if rpm < MIN_SPEED or rpm > MAX_SPEED:
            raise ValueError(f"{rpm} is outside of the range. Speed must be within 0 and 310 inclusive.")
        
        self._send(f"OUT_SP_4 {rpm}\r\n")
        
        self.speed = rpm
        print(f"Setting stirrer speed set to {rpm} RPM")
        
    def get_speed(self) -> int:
        command = f"IN_PV_4\r\n"
        
        self._send(command)
        
        response = self.ser.readline().decode('ascii').strip()
        int_response = int(response)
        
        print(f"Stirrer speed is {int_response}")
        
        return(int_response)