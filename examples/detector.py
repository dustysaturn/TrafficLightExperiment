import threading
import time
from datetime import datetime
import cv2
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt

class SubtractionMethod(Enum):
    KNN = 1
    MOG2 = 2

class ColourDetector():
    def __init__(self, camera, subtraction_method, record=True):
        self.cam = cv2.VideoCapture(camera)
        self.record = record
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))
        self.record = record
        if self.record:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fourcc = cv2.VideoWriter.fourcc(*'mp4v')
            self.out = cv2.VideoWriter(f'experiment_{timestamp}.mp4', fourcc, 20.0, (1920, 1080))
        
        self.method = subtraction_method
        self.mask = None
        self.frame = None
        self.colourName = None
        self.colourRGB = None
        self.vialPresent = False
        self.history = {"Yellow": [], "Red": [], "Green": [], "Seconds": []}
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
        if self.thread.is_alive():
            self.thread.join()
        self.out.release()
        self.cam.release()
        
    def loop(self):
        while(self.running):
            ret, frame = self.cam.read()
            
            if not ret:
                self.running = False
                
            if self.record:
                self.out.write(frame)

            if self.vialPresent:
                self.mask = self.subtractor.apply(frame)
                
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                detected = None
                
                colours = [
                    ("Yellow", np.array([10, 100, 100], dtype=np.uint8), np.array([24, 255, 255], dtype=np.uint8), (255, 255, 0)),
                    ("Red", (np.array([0, 120, 70], dtype=np.uint8), np.array([170, 120, 70], dtype=np.uint8)), (np.array([10, 255, 255], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8)), (255, 0, 0)), 
                    ("Green", np.array([25, 52, 72], dtype=np.uint8), np.array([102, 255, 255], dtype=np.uint8), (0, 255, 0)),
                ]
                
                self.history["Seconds"].append(time.time() - self.start_time)
                            
                for (name, lower, upper, colour) in colours:
                    if name == "Red":
                        red_1 = cv2.inRange(hsv, lower[0], upper[0])
                        red_2 = cv2.inRange(hsv, lower[1], upper[1])
                        colour_mask = cv2.bitwise_or(red_1, red_2)
                    else:
                        colour_mask = cv2.inRange(hsv, lower, upper)
                        
                    combined = cv2.bitwise_and(colour_mask, self.mask)
                    count = np.count_nonzero(combined)
                    
                    self.history[name].append(count)
                    
                    if count > 10000 and detected is None:
                        detected = name
                        self.colourName = detected
                        self.colourRGB = colour
                        self.frame = frame
            else:
                time.sleep(0.5)
                    
if __name__ == "__main__":
    detect = ColourDetector("./examples/colour_change.mp4", SubtractionMethod.KNN)
    detect.vialPresent = True
    detect.start()

    plt.ion()
    fig, ax = plt.subplots()
    lines = {
        "Yellow": ax.plot([], [], color='yellow', label="Yellow")[0],
        "Red": ax.plot([], [], color='red', label="Red")[0],
        "Green": ax.plot([], [], color='green', label="Green")[0],
    }
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Pixel count")
    ax.legend(loc='upper left')

    while detect.running:
        if detect.frame is not None:
            display = detect.frame.copy()
            cv2.putText(
                display, 
                f"Colour:{detect.colourName}", 
                (10, 50), 
                cv2.FONT_HERSHEY_PLAIN, 
                2, 
                detect.colourRGB, 
                3)
            cv2.imshow("Detection", display)
            
            s_len = len(detect.history["Seconds"])
            g_len = len(detect.history["Green"])
            o_len = len(detect.history["Yellow"])
            r_len = len(detect.history["Red"])

            if s_len > 0 and s_len == g_len == o_len == r_len:
                view_window = -50
                x_data = detect.history["Seconds"][view_window:]
                
                for name in ["Yellow", "Red", "Green"]:
                    lines[name].set_data(x_data, detect.history[name][view_window:])
            
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    cv2.destroyAllWindows()
    detect.end()