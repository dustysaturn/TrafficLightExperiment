import threading
import time
from datetime import datetime
import cv2
from enums import SubtractionMethod
import numpy as np
import json
import time
import matplotlib
import matplotlib.pyplot as plt
import os

# bus 003 device 005 id 046d: 08e5 logitech inc hd pro webcam c920

class ColourDetector():
    def __init__(self, vial_cam, main_cam, subtraction_method):
        self.lock = threading.Lock()
        self.cam = cv2.VideoCapture(vial_cam)
                            
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                
        self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.top_left = (int(self.width * (2/5)), int(self.height * (1/3)))
        self.bottom_right = (int(self.width * (3/5)), int(self.height * (2/3)))
        
        self.fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        
        self.cam.set(cv2.CAP_PROP_FOURCC, self.fourcc)
            
        # INTEGRATE
        self.main_cam = cv2.VideoCapture(main_cam)
        self.main_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.main_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.main_width = int(self.main_cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.main_height = int(self.main_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.main_cam.set(cv2.CAP_PROP_FOURCC, self.fourcc)
        
        self.masked_out = None
        self.graph_out = None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not os.path.exists('videos'):
            os.makedirs('videos')
        
        if not os.path.exists(f'videos/{timestamp}'):
            os.makedirs(f'videos/{timestamp}')
            
        self.folder = f'./videos/{timestamp}'
        
        # Switch to mp4v for linux
        self.out = cv2.VideoWriter(f'{self.folder}/raw.mp4', self.fourcc, 20.0, (self.width, self.height))
        
        if not self.out.isOpened():
            print("ERROR: VIAL_VideoWriter failed to open. Check your codec, file path, and resolution.")
        else:
            print("SUCCESS: VIAL_VideoWriter is ready to record.")
                            
        # INTEGRATE
        self.main_out = cv2.VideoWriter(f'{self.folder}/main.mp4', self.fourcc, 20.0, (self.main_width, self.main_height))

        if not self.main_out.isOpened():
            print("ERROR: MAIN_VideoWriter failed to open. Check your codec, file path, and resolution.")
        else:
            print("SUCCESS: MAIN_VideoWriter is ready to record.")

        self.method = subtraction_method
        self.mask = None
        self.masks = {}
        self.frame = None
        self.colourName = "None"
        self.colourRGB = (255, 255, 255)
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

        self.visualise_thread = threading.Thread(target=self.visualise, daemon=True)
        self.visualise_thread.start()
    
    def end(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
            
        if self.visualise_thread.is_alive():
            self.visualise_thread.join()
            
        for writer in [self.out, self.main_out, self.masked_out, self.graph_out]:
            if writer is not None:
                writer.release()
        
    def loop(self):
        while(self.running):
            ret, frame = self.cam.read()
            main_ret, main_frame = self.main_cam.read()
                                    
            if not (ret and main_ret):
                self.running = False
                continue
                        
            with self.lock:
                self.frame = frame.copy()
                self.main_frame = main_frame.copy()
                
            self.out.write(frame)
            self.main_out.write(main_frame)

            if self.vialPresent:
                cropped = frame[self.top_left[1]:self.bottom_right[1], self.top_left[0]:self.bottom_right[0]]
                
                self.mask = self.subtractor.apply(cropped)
                hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
                            
                detected = None
                
                colours = [
                    ("Yellow", np.array([10, 100, 100], dtype=np.uint8), np.array([24, 255, 255], dtype=np.uint8), (255, 255, 0)),
                    ("Red", (np.array([0, 120, 70], dtype=np.uint8), np.array([170, 120, 70], dtype=np.uint8)), (np.array([10, 255, 255], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8)), (255, 0, 0)), 
                    ("Green", np.array([25, 52, 72], dtype=np.uint8), np.array([102, 255, 255], dtype=np.uint8), (0, 255, 0)),
                ]
                
                self.masks = { }
                kernel = np.ones((5, 5), "uint8")
                            
                for (name, lower, upper, colour) in colours:
                    if name == "Red":
                        red_1 = cv2.inRange(hsv, lower[0], upper[0])
                        red_2 = cv2.inRange(hsv, lower[1], upper[1])
                        colour_mask = cv2.bitwise_or(red_1, red_2)
                    else:
                        colour_mask = cv2.inRange(hsv, lower, upper)
                
                    self.masks[name] = cv2.dilate(colour_mask, kernel)
                        
                    combined = cv2.bitwise_and(colour_mask, self.mask)
                    count = np.count_nonzero(combined)
                    
                    with self.lock:
                        self.history["Seconds"].append(time.time() - self.start_time)
                        self.history[name].append(count)
                    
                    if count > 10000 and detected is None:
                        detected = name
                        self.colourName = detected
                        self.colourRGB = colour
                        with self.lock:
                            self.frame = frame.copy()
            else:
                time.sleep(0.5)
                
    def getFolder(self) -> str:
        return self.folder
    
    def drawContour(self, colourName, frame):
        if self.masks is None or colourName not in self.masks:
            return frame
            
        contours, _ = cv2.findContours(self.masks[colourName], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:            
            if (cv2.contourArea(contour) > 300):
                x, y, w, h = cv2.boundingRect(contour)
                
                new_x = x + self.top_left[0]
                new_y = y + self.top_left[1]
                
                cv2.rectangle(frame, (new_x, new_y), (new_x + w, new_y + h), (0, 0, 255), 2)
                cv2.putText(frame, f"{colourName}", (new_x, new_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
        
        return frame
    
    # INTEGRATE
    def change_state(self, state):
        curr = time.time()
        time = curr - self.start_time
        print(state)
        
        with open(f"{self.folder}/state.txt", 'a') as file:
            file.write(f"{state} {str(time)}\n")
            
                
    def visualise(self):
        self.vialPresent = True

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
        
        def get_plot_image(figure):
            figure.canvas.draw()

            image = np.array(figure.canvas.renderer.buffer_rgba(), dtype=np.uint8)

            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)         

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:    
            while self.running:
                if self.frame is not None:
                    display = self.frame.copy()
                    cv2.putText(display, f"Colour:{self.colourName}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, self.colourRGB, 3)            
                    
                    main_display = self.main_frame.copy()
                    
                    cv2.imshow("Colour detection", main_display)
                    
                    self.drawContour(self.colourName, display)
                    cv2.rectangle(display, self.top_left, self.bottom_right,  (255, 0, 255), 3)
                            
                    if self.masked_out is None:
                        height, width, _ = display.shape
                        self.masked_out = cv2.VideoWriter(f'{self.folder}/masked.mp4', self.fourcc, 10.0, (width, height))

                    self.masked_out.write(display)
                                
                    seconds = list(self.history["Seconds"])
                    yellow = list(self.history["Yellow"])
                    red = list(self.history["Red"])
                    green = list(self.history["Green"])
                    
                    min_length = min(len(seconds), len(yellow), len(red), len(green))

                    if min_length > 0:
                        view_window = -100
                        x_data = seconds[:min_length][view_window:]
                                        
                        lines["Yellow"].set_data(x_data, yellow[:min_length][view_window:])
                        lines["Red"].set_data(x_data, red[:min_length][view_window:])
                        lines["Green"].set_data(x_data, green[:min_length][view_window:])
                    
                        ax.relim()
                        ax.autoscale_view()
                        
                        plot_frame = get_plot_image(fig)
                        
                        if self.graph_out is None:
                            height, width, _ = plot_frame.shape
                            self.graph_out = cv2.VideoWriter(f'{self.folder}/graph.mp4', self.fourcc, 10.0, (width, height))

                        self.graph_out.write(plot_frame)
                        
                        cv2.imshow("Colour Detection", plot_frame)
                        cv2.imshow("Colour Detection", plot_frame)
                
                k = cv2.waitKey(1)
                if k == 27:
                    break
            
                time.sleep(0.1)
        finally:
            # INTEGRATE
            with open(f"{self.folder}/colour-history", 'w') as file:
                json.dump(self.history, file, indent=4)
            
            # if combined_out:
            #     combined_out.release()
            cv2.destroyAllWindows()