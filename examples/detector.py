import threading
import time
import cv2
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt

class SubtractionMethod(Enum):
    KNN = 1
    MOG2 = 2

class ColourDetector():
    def __init__(self, camera, subtraction_method):
        self.cam = cv2.VideoCapture(camera)
        self.method = subtraction_method
        self.mask = None
        self.frame = None
        self.colour_name = None
        self.colour_rbg = None
        self.history = {"Green": [], "Orange": [], "Red": [], "Seconds": []}
        self.start_time = time.time()
        
        if self.method == SubtractionMethod.KNN:
            self.subtractor = cv2.createBackgroundSubtractorKNN()
        elif self.method == SubtractionMethod.MOG2:
            self.subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        else:
            raise ValueError("Invalid subtraction method provided")

    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()
    
    def end(self):
        self.running = False
        self.thread.join()
        self.cam.release()
        
    def loop(self):
        
        while(self.running):
            ret, frame = self.cam.read()
            
            if not ret:
                raise ValueError("Can't receive from stream")
        
            self.mask = self.subtractor.apply(frame)
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            detected = None
            
            colours = [
                ("Green", np.array([25, 52, 72], dtype=np.uint8), np.array([102, 255, 255], dtype=np.uint8), (0, 255, 0)),
                ("Orange", np.array([10, 100, 100], dtype=np.uint8), np.array([34, 255, 255], dtype=np.uint8), (0, 165, 255)),
                ("Red", np.array([136, 87, 111], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8), (255, 0, 0)), 
            ]
            
            self.history["Seconds"].append(self.start_time - time.time())
                        
            for (name, lower, upper, colour) in colours:
                colour_mask = cv2.inRange(hsv, lower, upper)
                combined = cv2.bitwise_and(colour_mask, self.mask)
                count = np.count_nonzero(combined)
                
                self.history[name].append(count)
                
                if count > 1000 and detected is None:
                    detected = name
                    self.colour_name = detected
                    self.colour_rgb = colour
                    self.frame = frame
                    
detect = ColourDetector("./colour_change.mp4", SubtractionMethod.KNN)
detect.start()

plt.ion()
fig, ax = plt.subplots()
lines = {
    "Green": ax.plot([], [], color='green', label="Green")[0],
    "Orange": ax.plot([], [], color='orange', label="Orange")[0],
    "Red": ax.plot([], [], color='red', label="Red")[0]
}
ax.set_xlabel("Time (s)")
ax.set_ylabel("Pixel count")
ax.legend(loc='upper left')

while detect.running:
    if detect.frame is not None:
        display = detect.frame.copy()
        cv2.putText(display, f"Colour:{detect.colour_name}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, detect.colour_rgb, 3)
        cv2.imshow("Detection", display)
        
        s_len = len(detect.history["Seconds"])
        g_len = len(detect.history["Green"])
        o_len = len(detect.history["Orange"])
        r_len = len(detect.history["Red"])

        if s_len > 0 and s_len == g_len == o_len == r_len:
            view_window = -50
            x_data = detect.history["Seconds"][view_window:]
            
            for name in ["Green", "Orange", "Red"]:
                lines[name].set_data(x_data, detect.history[name][view_window:])
        
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
cv2.destroyAllWindows()
detect.end()