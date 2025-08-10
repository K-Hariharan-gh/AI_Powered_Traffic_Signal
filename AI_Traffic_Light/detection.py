# detection.py
import cv2
from ultralytics import YOLO
from config import YOLO_MODEL_NAME, DETECTION_CONFIDENCE, VEHICLE_CLASSES, LANE_ZONES
import numpy as np

class Detector:
    def __init__(self, model_name=YOLO_MODEL_NAME, conf_thresh=DETECTION_CONFIDENCE):
        self.model = YOLO(model_name)  # will download model if not present
        self.conf_thresh = conf_thresh

    def detect(self, frame):
        """
        Run YOLO on the frame and return list of detections.
        Each detection: dict {'bbox': (x1,y1,x2,y2), 'class_name': str, 'conf': float}
        """
        # ultralytics accepts BGR numpy array (OpenCV) directly
        results = self.model.predict(frame, imgsz=(640, 640), conf=self.conf_thresh, verbose=False)
        detections = []
        # results is a list (one result per image). We used single frame.
        r = results[0]
        if r.boxes is None:
            return detections

        for box, cls, conf in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist()):
            x1, y1, x2, y2 = [int(v) for v in box]
            class_idx = int(cls)
            # get class name from model.names
            class_name = r.names[class_idx] if hasattr(r, "names") else str(class_idx)
            if class_name in VEHICLE_CLASSES:
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "class_name": class_name,
                    "conf": float(conf)
                })
        return detections

def assign_to_lanes(detections, lane_zones=LANE_ZONES):
    """
    Assign detected bboxes to lanes by checking bbox center inside zone.
    Returns counts dict and mapping of detection -> lane (for debug if needed).
    """
    counts = {k: 0 for k in lane_zones.keys()}
    mapping = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        assigned = None
        for lane_name, (lx1, ly1, lx2, ly2) in lane_zones.items():
            if lx1 <= cx <= lx2 and ly1 <= cy <= ly2:
                counts[lane_name] += 1
                assigned = lane_name
                break
        mapping.append((det, assigned))
    return counts, mapping
