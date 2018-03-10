from unittest import TestCase
from Indicators.SimpleMovingAverage import SMA


class TestSMA(TestCase):
    def test_tick(self):
        sma = SMA(length=10)

        mean = 0

        for i in range(0, 10):
            mean = sma.tick(10)

        self.assertEqual(mean, 10)

        for i in range(0, 10):
            print(i)
            mean = sma.tick(i)

        self.assertEqual(mean, 4.5)

    def test_add_tick(self):
        sma = SMA(length=10)
        for i in range(0, 10):
            sma.add_tick(10)

        self.assertEqual(len(sma.data), 10)

        for i in range(0, 10):
            sma.add_tick(10)

        self.assertEqual(len(sma.data), 10)
