# timer.py
import time

class SimpleTimer:
    def __init__(self, duration_s):
        self.duration = duration_s
        self.start_t = None

    def start(self):
        self.start_t = time.time()

    def elapsed(self):
        if self.start_t is None:
            return 0
        return time.time() - self.start_t

    def remaining(self):
        if self.start_t is None:
            return self.duration
        return max(0, self.duration - (time.time() - self.start_t))

    def is_done(self):
        return self.remaining() <= 0
