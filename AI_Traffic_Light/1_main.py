# 1_main.py
import time
import cv2
from yolo_detection import detect_cars           # returns list of lane ids detected, e.g. [1,3]
from utils_dl import draw_lane_zones     # optional helper (not required)
from config import FRAME_WIDTH, FRAME_HEIGHT

# --- Controller parameters ---
GREEN_DURATION = 15.0   # seconds
YELLOW_DURATION = 3.0   # seconds

# Allowed pairs
PAIR_A = (1, 3)   # lanes that can be green together
PAIR_B = (2, 4)

LANES = [1, 2, 3, 4]

# state: "idle" (all red), "green" (active_pair green), "yellow" (active_pair yellow)
state = "idle"
active_pair = None
green_end_time = None
yellow_end_time = None

# Track first detection time for priority (None if no waiting)
waiting_since = {1: None, 2: None, 3: None, 4: None}

# Signal states: "RED", "GREEN", "YELLOW"
signal_states = {1: "RED", 2: "RED", 3: "RED", 4: "RED"}

# Helper: set states for pair
def set_pair_state(pair, new_state):
    for l in pair:
        signal_states[l] = new_state

def all_red():
    for l in LANES:
        signal_states[l] = "RED"

def choose_pair_from_waiting():
    """
    Decide which pair to activate based on waiting_since timestamps and rules:
    - If consecutive lanes (1&2 or 3&4) are BOTH waiting -> priority to earlier detection.
    - Else if BOTH pairs have waiting lanes (but not consecutive conflict) -> allow both pairs.
    - Else if only one pair has waiting lanes -> activate that pair.
    - Else -> None (no waiting)
    """
    now = time.time()

    # Build set of waiting lanes (still present)
    waiting = {l for l, t in waiting_since.items() if t is not None}

    if not waiting:
        return None

    # Check consecutive conflicts first
    # consecutive pairs considered: (1,2) and (3,4)
    if 1 in waiting and 2 in waiting:
        # priority to earlier
        return (1, 3) if waiting_since[1] <= waiting_since[2] else (2, 4)
    if 3 in waiting and 4 in waiting:
        return (3, 1) if waiting_since[3] <= waiting_since[4] else (4, 2)
        # note: returned pair uses lane->its allowed pair

    # Now check if both allowed pairs have waiting lanes
    pairA_has = any(l in waiting for l in PAIR_A)
    pairB_has = any(l in waiting for l in PAIR_B)

    if pairA_has and pairB_has:
        # No consecutive conflict — allow both pairs (i.e., both sets green)
        return PAIR_A + PAIR_B  # tuple of four lanes (1,3,2,4) order doesn't matter

    # If only pairA has waiting lanes
    if pairA_has:
        return PAIR_A

    if pairB_has:
        return PAIR_B

    # If there's a single lane waiting but not in pairs above (shouldn't happen), pick that lane's pair
    # pick earliest waiting lane
    earliest = min(((l, t) for l, t in waiting_since.items() if t is not None), key=lambda x: x[1])[0]
    # map to pair
    return PAIR_A if earliest in PAIR_A else PAIR_B

# Initialize camera
# Try DirectShow backend on Windows for reliability
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    # fallback
    cap = cv2.VideoCapture(0)

# Optionally force frame size from config
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

print("Starting traffic controller. All signals RED.")

try:
    while True:
        now = time.time()
        ret, frame = cap.read()
        if not ret:
            # camera read failed — small wait, continue
            time.sleep(0.1)
            continue

        # --- Detection --- 
        # detect_cars should return a list of lane ids where vehicles exist in this frame (e.g. [1,3])
        detected_lanes = detect_cars(frame) or []

        # Update waiting_since timestamps:
        # - If detected now and not already waiting, set waiting_since to now
        # - If not detected now AND lane is not active green, clear waiting_since (we require presence to keep request)
        for l in LANES:
            if l in detected_lanes:
                if waiting_since[l] is None:
                    waiting_since[l] = now
            else:
                # If the lane is currently green or yellow (being served), keep its waiting_since until after its cycle finishes.
                # Otherwise, clear the waiting request (car left).
                if signal_states[l] == "RED":
                    waiting_since[l] = None

        # --- State machine ---
        if state == "idle":
            # If currently no green, check if any waiting lanes exist to start a cycle
            next_pair = choose_pair_from_waiting()
            if next_pair:
                # activate next_pair
                # next_pair may be a 2-lane tuple (pair) or 4-lane tuple (both pairs)
                active_pair = tuple(next_pair)
                set_pair_state(active_pair, "GREEN")
                green_end_time = now + GREEN_DURATION
                state = "green"
                print(f"Starting GREEN for lanes {active_pair} (until {green_end_time:.1f})")
            else:
                # remain all red
                all_red()

        elif state == "green":
            # if green time elapsed -> switch to yellow
            if now >= green_end_time:
                set_pair_state(active_pair, "YELLOW")
                yellow_end_time = now + YELLOW_DURATION
                state = "yellow"
                print(f"GREEN ended. YELLOW for lanes {active_pair} (until {yellow_end_time:.1f})")
            else:
                # remain green (nothing else interrupts; detection requests will be queued)
                pass

        elif state == "yellow":
            if now >= yellow_end_time:
                # finish cycle: set served lanes to RED and clear their waiting_since
                set_pair_state(active_pair, "RED")
                for l in active_pair:
                    # clear served wait request so same car won't be re-served unless new detection
                    waiting_since[l] = None
                active_pair = None
                state = "idle"
                print("Cycle finished. All served lanes set to RED. Back to idle.")
            else:
                # still in yellow
                pass

        # --- visualization overlay ---
        # draw quadrant split lines
        h, w = frame.shape[:2]
        cv2.line(frame, (w//2, 0), (w//2, h), (255,255,255), 2)
        cv2.line(frame, (0, h//2), (w, h//2), (255,255,255), 2)

        # show detected counts simple (we'll mark 1..4 counts as 0/1)
        counts = {l: (1 if l in detected_lanes else 0) for l in LANES}
        cv2.putText(frame, f"lane_1: {counts[1]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.putText(frame, f"lane_2: {counts[2]}", (w//2+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.putText(frame, f"lane_3: {counts[3]}", (10, h//2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.putText(frame, f"lane_4: {counts[4]}", (w//2+10, h//2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

        # show signals as small circles top-left area
        # map lane->position
        pos = {1: (50, 50), 2: (w-100, 50), 3: (50, h-100), 4: (w-100, h-100)}
        color_map = {"RED": (0,0,255), "YELLOW": (0,255,255), "GREEN": (0,255,0)}
        for l in LANES:
            col = color_map.get(signal_states[l], (100,100,100))
            cv2.circle(frame, pos[l], 24, col, -1)
            cv2.putText(frame, f"lane_{l}", (pos[l][0]-30, pos[l][1]+40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

        # show remaining time if in green or yellow
        if state == "green":
            rem = int(max(0, green_end_time - now))
            cv2.putText(frame, f"GREEN remaining: {rem}s", (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        elif state == "yellow":
            rem = int(max(0, yellow_end_time - now))
            cv2.putText(frame, f"YELLOW remaining: {rem}s", (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
        else:
            cv2.putText(frame, "All RED - waiting for vehicle", (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        # show frame
        cv2.imshow("Traffic Control", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:   # ESC to quit
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Stopped.")
