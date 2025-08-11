import time

# Initial state: all red
signal_states = {1: "RED", 2: "RED", 3: "RED", 4: "RED"}
green_timer = {1: 0, 2: 0, 3: 0, 4: 0}

def update_signals(active_lanes):
    global signal_states, green_timer

    # Check if any lane's green time expired
    for lane in green_timer:
        if green_timer[lane] > 0 and time.time() > green_timer[lane]:
            signal_states[lane] = "RED"

    # If no greens are active, give green to detected lanes
    if all(state == "RED" for state in signal_states.values()) and active_lanes:
        lane = active_lanes[0]  # Pick first detected
        pair = (lane, 3) if lane == 1 else (lane, 4) if lane == 2 else (lane, 1) if lane == 3 else (lane, 2)

        for l in pair:
            signal_states[l] = "GREEN"
            green_timer[l] = time.time() + 15  # 15s green

    return signal_states
