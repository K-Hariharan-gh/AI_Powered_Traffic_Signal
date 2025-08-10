# config.py
# Edit lane coordinates here to match your camera view.
# Coordinates are in (x1, y1, x2, y2) format relative to the captured frame.

# Recommended: Run once with draw_lanes to find coordinates, or tweak visually.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DETECTION_CONFIDENCE = 0.35  # YOLO detection threshold

# Lanes: define rectangles covering each lane (top-left x,y, bottom-right x,y)
# Example for a 4-way intersection (adjust to match your camera):
LANE_ZONES = {
    "lane_1": [0, 0, 320, 240],       # top-left quadrant
    "lane_2": [320, 0, 640, 240],     # top-right
    "lane_3": [0, 240, 320, 480],     # bottom-left
    "lane_4": [320, 240, 640, 480],   # bottom-right
}

# GUI / timing defaults (seconds)
MIN_GREEN = 3
MAX_GREEN = 12

# YOLO model: you can use 'yolov8n.pt' or 'yolov8n' (ultralytics will download)
YOLO_MODEL_NAME = "yolov8n.pt"

# Classes from COCO we accept as vehicles
# Using YOLO's numeric indices if you want to filter by cls index,
# but ultralytics returns class names so we'll check names.
VEHICLE_CLASSES = {"car", "truck", "bus", "motorbike", "bicycle"}  # bicycle optional
