import json

from Events.IEvent import IEvent
from Models.Candle import Candle


class CandleEvent(IEvent):
    def __init__(self, instrument, time, open, high, low, close, volume):
        self.type = 'TICK'
        self.instrument = instrument
        self.time = time
        self.candle = Candle(open=open, high=high, low=low, close=close)
        self.volume = volume

    def current_bid_price(self):
        return self.candle.close

    def current_ask_price(self):
        return self.candle.close

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    @staticmethod
    def from_json(tick):
        return CandleEvent(tick['instrument'], tick['time'], tick['candle']['open'], tick['candle']['high']
                           , tick['candle']['low'] , tick['candle']['close'], tick['volume'])
