import numpy as np


class SMA:
    def __init__(self, length=20):
        self.length = length
        self.data = []

    def tick(self, current_close_price):
        self.add_tick(current_close_price)
        return np.max(self.data)

    def add_tick(self, current_close_price):
        self.data.append(current_close_price)

        if len(self.data) > self.length:
            self.data = self.data[-self.length:]