import threading
import time
from datetime import datetime
import cv2
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt

# bus 003 device 005 id 046d: 08e5 logitech inc hd pro webcam c920

class SubtractionMethod(Enum):
    KNN = 1
    MOG2 = 2

class ColourDetector():
    def __init__(self, camera, subtraction_method, record=True):
        self.lock = threading.Lock()
        self.cam = cv2.VideoCapture(camera)
        print(f"Width: {int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))}")
        print(f"Height: {int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))}")    
        self.top_left = (360, 368)
        self.bottom_right = (720, 1104)
        
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
            
            # frame = frame[self.top_left[1]:self.bottom_right[1], self.top_left[0]:self.bottom_right[0]]
            
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
                self.masks = { }
                self.residual_masks = {}
                kernel = np.ones((5, 5), "uint8")
                            
                for (name, lower, upper, colour) in colours:
                    if name == "Red":
                        red_1 = cv2.inRange(hsv, lower[0], upper[0])
                        red_2 = cv2.inRange(hsv, lower[1], upper[1])
                        colour_mask = cv2.bitwise_or(red_1, red_2)
                    else:
                        colour_mask = cv2.inRange(hsv, lower, upper)
                
                    self.masks[name] = cv2.dilate(colour_mask, kernel)
                    self.residual_masks[name] = cv2.bitwise_and(frame, frame, mask = self.masks[name])
                        
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
    
    def drawContour(self, colourName, frame):
        if self.masks is None or colourName not in self.masks:
            return frame
            
        contours, _ = cv2.findContours(self.masks[colourName], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:            
            if (cv2.contourArea(contour) > 300):
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, f"{colourName}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
        
        return frame
                    
if __name__ == "__main__":
    colours = ("Yellow", "Red", "Green")
    detect = ColourDetector("./colour_change.mp4", SubtractionMethod.MOG2)
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
            cv2.putText(display, f"Colour:{detect.colourName}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, detect.colourRGB, 3)            
            
            detect.drawContour(detect.colourName, display)
            cv2.rectangle(display, detect.top_left, detect.bottom_right,  (255, 0, 255), 3)
            
            cv2.imshow("Detection", display)
            
            seconds = list(detect.history["Seconds"])
            yellow = list(detect.history["Yellow"])
            red = list(detect.history["Red"])
            green = list(detect.history["Green"])
            
            s_len = len(seconds)
            g_len = len(green)
            y_len = len(yellow)
            r_len = len(red)

            if s_len > 0 and s_len == g_len == y_len == r_len:
                view_window = -50
                x_data = seconds[view_window:]
                                    
                lines["Yellow"].set_data(x_data, yellow[view_window:])
                lines["Red"].set_data(x_data, red[view_window:])
                lines["Green"].set_data(x_data, green[view_window:])
            
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    cv2.destroyAllWindows()
    detect.end()