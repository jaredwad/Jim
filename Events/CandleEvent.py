import json
from datetime import datetime

from Events.IEvent import IEvent
from Models.Candle import Candle
from Models.Duration import Duration


class CandleEvent(IEvent):
    def __init__(self, instrument, time, duration, open, high, low, close, volume):
        self.type = 'CANDLE'
        self.instrument = instrument
        self.time = time
        self.duration = duration
        self.candle = Candle(open=open, high=high, low=low, close=close)
        self.volume = volume

    def current_bid_price(self):
        return self.candle.close

    def current_ask_price(self):
        return self.candle.close

    def to_json(self):
        def stuff_to_string(data):
            if isinstance(data, Duration):
                return data.name
            elif isinstance(data, datetime):
                return data.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                return data.__dict__

        return json.dumps(self, default=stuff_to_string, sort_keys=True)

    @staticmethod
    def from_json(tick):
        return CandleEvent(tick['instrument'], datetime.strptime(tick['time'], "%Y-%m-%dT%H:%M:%S"), tick['duration']
                           , tick['candle']['open'], tick['candle']['high'], tick['candle']['low']
                           , tick['candle']['close'], tick['volume'])
