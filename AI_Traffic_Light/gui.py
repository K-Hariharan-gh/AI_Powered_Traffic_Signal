# gui.py
import tkinter as tk
import threading
from timer import SimpleTimer
from config import LANE_ZONES, MIN_GREEN, MAX_GREEN

class TrafficGUI:
    def __init__(self, shared_state):
        """
        shared_state: object with attribute latest_counts (dict) updated by main loop
        """
        self.shared_state = shared_state
        self.root = tk.Tk()
        self.root.title("Virtual Traffic Lights - AI Demo")

        self.canvas = tk.Canvas(self.root, width=420, height=420, bg="black")
        self.canvas.pack(padx=8, pady=8)

        # layout: place 4 circles to represent four lanes
        self.lane_positions = {
            "lane_1": (100, 80),
            "lane_2": (320, 80),
            "lane_3": (100, 320),
            "lane_4": (320, 320),
        }

        self.light_items = {}
        for name, (x, y) in self.lane_positions.items():
            # draw gray circle as background
            item = self.canvas.create_oval(x-40, y-40, x+40, y+40, fill="gray", outline="white", width=2)
            text = self.canvas.create_text(x, y+60, text=name, fill="white")
            self.light_items[name] = item

        # Info labels
        self.info_label = tk.Label(self.root, text="Counts: initializing...", font=("Arial", 10))
        self.info_label.pack(pady=6)

        self.timer_label = tk.Label(self.root, text="Timer: --", font=("Arial", 12))
        self.timer_label.pack()

        # control state
        self.current_green = None
        self.timer = None

        # run polling
        self.root.after(500, self.control_loop)

    def start(self):
        # run Tk mainloop in current thread (we'll call start() from a thread)
        self.root.mainloop()

    def control_loop(self):
        counts = getattr(self.shared_state, "latest_counts", None)
        if counts is None:
            self.root.after(500, self.control_loop)
            return

        # Show counts in label
        counts_text = ", ".join([f"{k}:{v}" for k, v in counts.items()])
        self.info_label.config(text="Counts: " + counts_text)

        # Decide which lane should be green
        # If no vehicles, cycle default short greens
        lane_order = list(counts.keys())
        max_lane = max(counts, key=lambda k: counts[k]) if any(counts.values()) else None

        if self.current_green is None or (self.timer is not None and self.timer.is_done()):
            # select next green based on max vehicles
            if max_lane and counts[max_lane] > 0:
                selected = max_lane
                # tune green time proportional to count
                cnt = counts[selected]
                green_time = min(MAX_GREEN, max(MIN_GREEN, 1 + int(cnt * 1.5)))
            else:
                # round-robin default: pick next lane
                if self.current_green is None:
                    selected = lane_order[0]
                else:
                    idx = lane_order.index(self.current_green)
                    selected = lane_order[(idx + 1) % len(lane_order)]
                green_time = MIN_GREEN

            self.current_green = selected
            self.timer = SimpleTimer(green_time)
            self.timer.start()

        # update lights visuals
        for lane in lane_order:
            item = self.light_items[lane]
            if lane == self.current_green:
                self.canvas.itemconfig(item, fill="green")
            else:
                self.canvas.itemconfig(item, fill="red")

        # show timer remaining
        rem = int(self.timer.remaining()) if self.timer else 0
        self.timer_label.config(text=f"Green: {self.current_green} | Remaining: {rem}s")

        # poll again
        self.root.after(400, self.control_loop)
