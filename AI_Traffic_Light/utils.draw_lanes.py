# draw_lanes.py
import cv2

def draw_lane_zones(frame, lane_zones, counts=None):
    """
    Overlay lane rectangles and optionally counts onto the frame.
    """
    overlay = frame.copy()
    for idx, (name, (x1, y1, x2, y2)) in enumerate(lane_zones.items(), start=1):
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{name}: {counts.get(name, 0) if counts else ''}"
        cv2.putText(overlay, label, (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return overlay
