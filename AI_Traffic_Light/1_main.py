import cv2
from ultralytics import YOLO
import tkinter as tk
import threading
import time

# Load YOLO model
model = YOLO("yolov8n.pt")  # small model for speed

# Tkinter GUI
root = tk.Tk()
root.title("AI Controlled Traffic Light")

canvas = tk.Canvas(root, width=200, height=400, bg="black")
canvas.pack()

# Draw initial traffic light
red_light = canvas.create_oval(50, 50, 150, 150, fill="grey")
yellow_light = canvas.create_oval(50, 160, 150, 260, fill="grey")
green_light = canvas.create_oval(50, 270, 150, 370, fill="grey")

current_light = "red"
last_switch_time = time.time()

# Function to update lights
def set_light(color):
    global current_light, last_switch_time
    canvas.itemconfig(red_light, fill="grey")
    canvas.itemconfig(yellow_light, fill="grey")
    canvas.itemconfig(green_light, fill="grey")

    if color == "red":
        canvas.itemconfig(red_light, fill="red")
    elif color == "yellow":
        canvas.itemconfig(yellow_light, fill="yellow")
    elif color == "green":
        canvas.itemconfig(green_light, fill="green")

    current_light = color
    last_switch_time = time.time()

# YOLO detection in a separate thread
def detect_vehicles():
    global current_light, last_switch_time

    cap = cv2.VideoCapture(0)  # laptop camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True)
        vehicle_detected = False

        for r in results:
            for c in r.boxes.cls:
                cls_name = model.names[int(c)]
                if cls_name in ["car", "motorbike", "bus", "truck"]:
                    vehicle_detected = True

        # AI traffic logic
        elapsed = time.time() - last_switch_time

        if vehicle_detected and current_light != "green":
            set_light("green")  # Turn green when cars present

        elif not vehicle_detected and elapsed >= 15:
            set_light("red")  # Switch to red if no vehicles for 15s

        cv2.imshow("Camera View", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start green at the beginning
set_light("green")

# Start detection thread
threading.Thread(target=detect_vehicles, daemon=True).start()

root.mainloop()
