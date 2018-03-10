from Indicators.Crossover import Crossover
from Indicators.SimpleMovingAverage import SMA


class CrossoverBot:
    def __init__(self):
        self.crossover = Crossover(first=SMA(20), second=SMA(60))
        self.age = 0
        self.previous = None
        self.current_position = 0
        self.money = 100000
        self.current_price = 0

    def tick(self, data):
        self.current_price = data

        current = self.crossover.tick(data)

        if self.age > 60:
            self.act(current, data)

        self.previous = current
        self.age += 1

    def act(self, buy, price):
        if self.previous == buy:  # Do nothing if the state hasn't changed
            pass

        self.close_all(price=price)

        if buy:
            print("Buying")
            self.buy(units=1000, price=price)
        else:
            print("Selling")
            self.sell(units=1000, price=price)

    def buy(self, units, price):
        self.money -= units * price
        self.current_position += units

    def sell(self, units, price):
        self.buy(units=-units, price=price)

    def close_all(self, price):
        self.buy(units=-self.current_position, price=price)

    def get_current_value(self):
        return self.money + self.current_position * self.current_price
