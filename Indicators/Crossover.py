from Indicators.SimpleMovingAverage import SMA


class Crossover:
    def __init__(self, first=None, second=None):
        if first is None:
            first = SMA(10)
        if second is None:
            second = SMA(20)

        self.first = first
        self.second = second

    def tick(self, data):
        fast_mean = self.first.tick(data)
        slow_mean = self.second.tick(data)

        return fast_mean > slow_mean  # True == BUY, False == SELL
