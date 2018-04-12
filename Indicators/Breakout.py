import numpy as np


class Breakout:
    def __init__(self, length=20):
        self.length = length
        self.data = []
        self.current_max = None
        self.current_min = None

    def tick(self, current_close_price):
        self.add_tick(current_close_price)
        self.current_max = np.max(self.data)
        self.current_min = np.min(self.data)

    def add_tick(self, current_close_price):
        self.data.append(current_close_price)

        if len(self.data) > self.length:
            self.data = self.data[-self.length:]

    def ready(self):
        return len(self.data) >= self.length