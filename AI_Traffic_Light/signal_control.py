import time

def set_signal_state(signal_states, lane, state):
    """Set the state for a given lane."""
    signal_states[lane] = state
    print(f"Lane {lane} → {state}")

def set_all_red(signal_states):
    """Set all lanes to RED."""
    for lane in signal_states:
        set_signal_state(signal_states, lane, "RED")

def run_signal_cycle(signal_states, lanes):
    """Run one cycle of green → yellow → red for given lanes."""
    # Green
    for lane in lanes:
        set_signal_state(signal_states, lane, "GREEN")
    time.sleep(15)

    # Yellow
    for lane in lanes:
        set_signal_state(signal_states, lane, "YELLOW")
    time.sleep(3)

    # Red
    for lane in lanes:
        set_signal_state(signal_states, lane, "RED")
